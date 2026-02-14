#!/usr/bin/env python3
"""
Instagram Automation Module
Posts to Instagram using Playwright (USE TEST ACCOUNT ONLY!)

Usage:
    from src.social.instagram import InstagramPoster
    poster = InstagramPoster()
    poster.post("Caption here", "/path/to/image.jpg")
"""

import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("   Run: pip install playwright && playwright install chromium")
    sys.exit(1)


class InstagramPoster:
    """Instagram posting automation using Playwright"""

    def __init__(self):
        self.email = os.getenv("INSTAGRAM_EMAIL")
        self.password = os.getenv("INSTAGRAM_PASSWORD")
        self.vault_path = Path(os.getenv("VAULT_PATH", "./vault"))

        if not self.email or not self.password:
            raise ValueError("INSTAGRAM_EMAIL and INSTAGRAM_PASSWORD required in .env")

    async def _post_async(self, caption: str, image_path: str, dry_run: bool = False) -> dict:
        """Post to Instagram asynchronously"""

        image = Path(image_path)
        if not image.exists():
            return {"success": False, "error": f"Image not found: {image_path}"}

        if dry_run:
            print(f"🔸 [DRY RUN] Would post to IG:")
            print(f"   Caption: {caption[:50]}...")
            print(f"   Image: {image_path}")
            return {"success": True, "dry_run": True, "caption": caption}

        result = {"success": False, "caption": caption, "image": str(image_path)}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print("📸 Opening Instagram...")
                await page.goto("https://www.instagram.com/", wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Login
                print("   Logging in...")
                await page.fill('input[name="username"]', self.email)
                await page.fill('input[name="password"]', self.password)
                await page.click('button[type="submit"]')
                await page.wait_for_timeout(5000)

                # Handle popups
                for _ in range(2):
                    try:
                        not_now = page.locator('text=Not Now')
                        if await not_now.is_visible(timeout=3000):
                            await not_now.click()
                            await page.wait_for_timeout(1000)
                    except:
                        pass

                print("   ✓ Logged in!")

                # Create post
                print("   Opening create post...")
                await page.click('[aria-label="New post"]')
                await page.wait_for_timeout(2000)

                # Upload image
                print(f"   Uploading: {image.name}...")
                file_input = page.locator('input[type="file"]')
                await file_input.set_input_files(str(image.absolute()))
                await page.wait_for_timeout(3000)

                # Next (twice to skip filters)
                print("   Processing...")
                await page.click('text=Next')
                await page.wait_for_timeout(2000)
                await page.click('text=Next')
                await page.wait_for_timeout(2000)

                # Caption
                print(f"   Adding caption...")
                await page.fill('textarea[aria-label="Write a caption..."]', caption)
                await page.wait_for_timeout(1000)

                # Share
                print("   Sharing...")
                await page.click('text=Share')
                await page.wait_for_timeout(5000)

                print("   ✅ Posted to Instagram!")
                result["success"] = True
                result["timestamp"] = datetime.now().isoformat()

            except Exception as e:
                print(f"   ❌ Error: {e}")
                result["error"] = str(e)
                await page.screenshot(path="instagram_error.png")
                print("   📸 Screenshot saved: instagram_error.png")

            finally:
                await browser.close()

        return result

    def post(self, caption: str, image_path: str, dry_run: bool = False) -> dict:
        """Post to Instagram (sync wrapper)"""
        return asyncio.run(self._post_async(caption, image_path, dry_run))

    def create_draft(self, topic: str, style: str = "engaging") -> Path:
        """Create draft and save to vault"""
        drafts_dir = self.vault_path / "Social_Media" / "Instagram_Drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic[:30].replace(" ", "_").lower()
        filename = f"IG_{timestamp}_{slug}.md"
        filepath = drafts_dir / filename

        content = f"""---
type: instagram_draft
topic: {topic}
style: {style}
created: {datetime.now().isoformat()}
status: pending
---

# Instagram Draft

**Topic:** {topic}
**Style:** {style}

---

## Caption:

[Scroll-stopping first line ✨]

[Value about {topic}]

[Question or CTA]

.
.
.

#AI #Tech #Innovation #Automation #Business

---

## Image Ideas:
- [ ] Product screenshot
- [ ] Quote graphic
- [ ] Behind-the-scenes
- [ ] Carousel

📋 COPY → ADD IMAGE → POST!
"""

        filepath.write_text(content, encoding="utf-8")
        return filepath


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Instagram Automation")
    parser.add_argument("--post", help="Caption text")
    parser.add_argument("--image", help="Image path (required for --post)")
    parser.add_argument("--draft", help="Create draft for topic")
    parser.add_argument("--style", default="engaging", help="Draft style")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually post")

    args = parser.parse_args()

    poster = InstagramPoster()

    if args.post:
        if not args.image:
            print("❌ --image required for posting!")
            sys.exit(1)
        print("=" * 50)
        print("📸 Instagram Poster")
        print("=" * 50)
        result = poster.post(args.post, args.image, args.dry_run)
        print(f"\nResult: {'✅ Success' if result['success'] else '❌ Failed'}")

    elif args.draft:
        filepath = poster.create_draft(args.draft, args.style)
        print(f"✅ Draft saved: {filepath}")

    else:
        parser.print_help()
