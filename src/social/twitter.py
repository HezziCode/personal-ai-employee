#!/usr/bin/env python3
"""
Twitter/X Automation Module
Posts tweets using Playwright (USE TEST ACCOUNT ONLY!)

Usage:
    from src.social.twitter import TwitterPoster
    poster = TwitterPoster()
    poster.post("Hello World!", dry_run=True)

    # CLI:
    python -m src.social.twitter --post "Tweet text" --dry-run
"""

import os
import sys
import asyncio
import argparse
from datetime import datetime
from pathlib import Path

# Add project root to path FIRST
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

try:
    from playwright.async_api import async_playwright
except ImportError as e:
    print("❌ Playwright not installed!")
    print("   Run: pip install playwright")
    print("   Then: playwright install chromium")
    print(f"\n   Error: {e}")
    sys.exit(1)

try:
    from src.utils.logging import log_action
    from src.utils.errors import TransientError, AuthError
except ImportError as e:
    print(f"❌ Import error: {e}")
    print(f"   sys.path: {sys.path[:3]}")
    sys.exit(1)


class TwitterPoster:
    """Twitter/X posting automation using Playwright"""

    def __init__(self):
        self.email = os.getenv("TWITTER_EMAIL")
        self.password = os.getenv("TWITTER_PASSWORD")
        self.vault_path = Path(os.getenv("VAULT_PATH", "./vault"))

        if not self.email or not self.password:
            raise ValueError("TWITTER_EMAIL and TWITTER_PASSWORD required in .env")

    async def _post_async(self, text: str, dry_run: bool = False) -> dict:
        """Post tweet asynchronously"""

        if len(text) > 280:
            return {"success": False, "error": f"Tweet too long: {len(text)}/280"}

        if dry_run:
            print(f"🔸 [DRY RUN] Would post: {text[:50]}...")
            return {"success": True, "dry_run": True, "text": text}

        result = {"success": False, "text": text}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                print("🐦 Opening Twitter...")
                await page.goto("https://twitter.com/login", wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Enter email
                print("   Entering email...")
                await page.fill('input[autocomplete="username"]', self.email)
                await page.click('text=Next')
                await page.wait_for_timeout(2000)

                # Handle username verification if needed
                try:
                    username_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
                    if await username_input.is_visible(timeout=3000):
                        print("   Username verification required...")
                        username = self.email.split('@')[0]
                        await username_input.fill(username)
                        await page.click('text=Next')
                        await page.wait_for_timeout(2000)
                except:
                    pass

                # Enter password
                print("   Entering password...")
                await page.fill('input[name="password"]', self.password)
                await page.click('text=Log in')
                await page.wait_for_timeout(3000)

                # Check login
                print("   Checking login status...")
                await page.wait_for_url("**/home", timeout=10000)
                print("   ✓ Logged in!")

                # Compose tweet
                print("   Opening compose box...")
                await page.click('[data-testid="SideNav_NewTweet_Button"]')
                await page.wait_for_timeout(1000)

                # Type tweet
                print(f"   Typing tweet: {text[:30]}...")
                await page.fill('[data-testid="tweetTextarea_0"]', text)
                await page.wait_for_timeout(500)

                # Post
                print("   Posting...")
                await page.click('[data-testid="tweetButton"]')
                await page.wait_for_timeout(3000)

                print("   ✅ Tweet posted!")
                result["success"] = True
                result["timestamp"] = datetime.now().isoformat()

            except Exception as e:
                print(f"   ❌ Error: {e}")
                result["error"] = str(e)
                try:
                    await page.screenshot(path="twitter_error.png")
                    print("   📸 Screenshot saved: twitter_error.png")
                except:
                    pass

            finally:
                await browser.close()

        return result

    def post(self, text: str, dry_run: bool = False) -> dict:
        """Post tweet (sync wrapper)"""
        start_time = datetime.now()
        result = asyncio.run(self._post_async(text, dry_run))
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Log action
        log_action(
            action_type="twitter_post",
            target="twitter",
            parameters={"text": text[:50], "dry_run": dry_run},
            result="success" if result.get("success") else "failure",
            error_code=None if result.get("success") else "POST_FAILED",
            error_message=result.get("error"),
            duration_ms=duration_ms,
            approval_status="human_approved" if not dry_run else "auto",
            vault_path=str(self.vault_path)
        )

        return result

    def create_draft(self, topic: str, style: str = "engaging") -> Path:
        """Create draft and save to vault"""
        drafts_dir = self.vault_path / "Social_Media" / "Twitter_Drafts"
        drafts_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        slug = topic[:30].replace(" ", "_").lower()
        filename = f"TWEET_{timestamp}_{slug}.md"
        filepath = drafts_dir / filename

        content = f"""---
type: twitter_draft
topic: {topic}
style: {style}
created: {datetime.now().isoformat()}
status: pending
char_limit: 280
---

# Twitter Draft

**Topic:** {topic}
**Style:** {style}

---

## Draft Content:

🔥 [Attention-grabbing hook about {topic}]

[Main value message]

👇 [Call to action]

#AI #Automation #Tech

---

## Checklist:
- [ ] Under 280 characters
- [ ] Hook is engaging
- [ ] CTA is clear
- [ ] Hashtags relevant

📋 COPY → PASTE IN TWITTER → POST!
"""

        filepath.write_text(content, encoding="utf-8")
        return filepath


# CLI Interface
def main():
    """Command line interface for Twitter posting"""
    parser = argparse.ArgumentParser(
        description="Twitter/X Automation",
        epilog="Examples:\n  python -m src.social.twitter --post 'Hello!' --dry-run\n  python -m src.social.twitter --draft 'AI Topic'",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--post", help="Tweet text to post (max 280 chars)")
    parser.add_argument("--draft", help="Create draft for topic")
    parser.add_argument("--style", default="engaging",
                       choices=["engaging", "professional", "casual"],
                       help="Draft style (default: engaging)")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--vault", help="Path to vault", default=os.getenv("VAULT_PATH", "./vault"))

    args = parser.parse_args()

    try:
        poster = TwitterPoster()

        if args.post:
            print("=" * 60)
            print("🐦 Twitter Poster")
            print("=" * 60)
            print(f"Text: {args.post}")
            print(f"Length: {len(args.post)}/280")
            print(f"Dry Run: {args.dry_run}")
            print("=" * 60)

            result = poster.post(args.post, args.dry_run)

            if result["success"]:
                print(f"\n✅ Success!")
                if result.get("timestamp"):
                    print(f"   Posted at: {result['timestamp']}")
            else:
                print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)

        elif args.draft:
            print("=" * 60)
            print("📝 Creating Twitter Draft")
            print("=" * 60)
            filepath = poster.create_draft(args.draft, args.style)
            print(f"✅ Draft saved: {filepath}")
            print(f"\n📋 Edit the file and manually post on Twitter")

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
