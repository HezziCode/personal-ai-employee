#!/usr/bin/env python3
"""
Instagram Auto Poster using Playwright
Posts to Instagram automatically (USE TEST ACCOUNT ONLY!)

Usage:
    python post_instagram.py --caption "Your caption" --image /path/to/image.jpg
    python post_instagram.py --caption "Hello!" --image photo.jpg --dry-run
"""

import os
import sys
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("   Run: pip install playwright")
    print("   Then: playwright install chromium")
    sys.exit(1)


async def post_instagram(caption: str, image_path: str, dry_run: bool = False) -> dict:
    """Post to Instagram using Playwright"""

    email = os.getenv("INSTAGRAM_EMAIL")
    password = os.getenv("INSTAGRAM_PASSWORD")

    if not email or not password:
        return {"success": False, "error": "INSTAGRAM_EMAIL and INSTAGRAM_PASSWORD required in .env"}

    # Verify image exists
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

            # Click login
            print("   Clicking login...")
            await page.click('text=Log in')
            await page.wait_for_timeout(1000)

            # Enter credentials
            print("   Entering email...")
            await page.fill('input[name="username"]', email)
            print("   Entering password...")
            await page.fill('input[name="password"]', password)
            await page.click('button[type="submit"]')
            await page.wait_for_timeout(5000)

            # Handle "Save Login Info" popup
            try:
                not_now = page.locator('text=Not Now')
                if await not_now.is_visible(timeout=3000):
                    await not_now.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            # Handle notifications popup
            try:
                not_now = page.locator('text=Not Now')
                if await not_now.is_visible(timeout=3000):
                    await not_now.click()
                    await page.wait_for_timeout(1000)
            except:
                pass

            print("   ✓ Logged in!")

            # Click create post (+ icon)
            print("   Opening create post...")
            await page.click('[aria-label="New post"]')
            await page.wait_for_timeout(2000)

            # Upload image
            print(f"   Uploading image: {image.name}...")
            file_input = page.locator('input[type="file"]')
            await file_input.set_input_files(str(image.absolute()))
            await page.wait_for_timeout(3000)

            # Click Next
            print("   Clicking Next...")
            await page.click('text=Next')
            await page.wait_for_timeout(2000)

            # Click Next again (skip filters)
            await page.click('text=Next')
            await page.wait_for_timeout(2000)

            # Enter caption
            print(f"   Adding caption: {caption[:30]}...")
            await page.fill('textarea[aria-label="Write a caption..."]', caption)
            await page.wait_for_timeout(1000)

            # Click Share
            print("   Sharing post...")
            await page.click('text=Share')
            await page.wait_for_timeout(5000)

            print("   ✅ Posted to Instagram!")
            result["success"] = True
            result["timestamp"] = datetime.now().isoformat()

        except Exception as e:
            print(f"   ❌ Error: {e}")
            result["error"] = str(e)

            screenshot_path = Path("instagram_error.png")
            await page.screenshot(path=str(screenshot_path))
            print(f"   📸 Screenshot saved: {screenshot_path}")

        finally:
            await browser.close()

    return result


def log_action(result: dict, vault_path: str = None):
    """Log the posting action"""
    vault = Path(vault_path or os.getenv("VAULT_PATH", "./vault"))
    logs_dir = vault / "Logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    log_file = logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

    import json
    logs = []
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except:
            logs = []

    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action": "instagram_post",
        "result": result
    })

    log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Post to Instagram via Playwright")
    parser.add_argument("--caption", required=True, help="Post caption")
    parser.add_argument("--image", required=True, help="Path to image file")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually post")
    parser.add_argument("--vault", help="Path to vault for logging")

    args = parser.parse_args()

    print("=" * 50)
    print("📸 Instagram Auto Poster")
    print("=" * 50)
    print(f"Caption: {args.caption[:50]}...")
    print(f"Image: {args.image}")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 50)

    result = asyncio.run(post_instagram(args.caption, args.image, args.dry_run))

    log_action(result, args.vault)

    if result["success"]:
        print("\n✅ Success!")
    else:
        print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
