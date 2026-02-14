#!/usr/bin/env python3
"""
Twitter/X Auto Poster using Playwright
Posts tweets automatically (USE TEST ACCOUNT ONLY!)

Usage:
    python post_tweet.py --text "Your tweet here"
    python post_tweet.py --text "Hello World!" --dry-run
"""

import os
import sys
import argparse
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Check for playwright
try:
    from playwright.async_api import async_playwright
except ImportError:
    print("❌ Playwright not installed!")
    print("   Run: pip install playwright")
    print("   Then: playwright install chromium")
    sys.exit(1)


async def post_tweet(text: str, dry_run: bool = False) -> dict:
    """Post a tweet using Playwright"""

    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")

    if not email or not password:
        return {"success": False, "error": "TWITTER_EMAIL and TWITTER_PASSWORD required in .env"}

    if dry_run:
        print(f"🔸 [DRY RUN] Would post: {text[:50]}...")
        return {"success": True, "dry_run": True, "text": text}

    result = {"success": False, "text": text}

    async with async_playwright() as p:
        # Launch browser (headless=False to see what's happening)
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            print("🐦 Opening Twitter...")
            await page.goto("https://twitter.com/login", wait_until="networkidle")
            await page.wait_for_timeout(2000)

            # Enter email
            print("   Entering email...")
            await page.fill('input[autocomplete="username"]', email)
            await page.click('text=Next')
            await page.wait_for_timeout(2000)

            # Check if username verification needed
            try:
                username_input = page.locator('input[data-testid="ocfEnterTextTextInput"]')
                if await username_input.is_visible(timeout=3000):
                    print("   Username verification required...")
                    # Extract username from email
                    username = email.split('@')[0]
                    await username_input.fill(username)
                    await page.click('text=Next')
                    await page.wait_for_timeout(2000)
            except:
                pass

            # Enter password
            print("   Entering password...")
            await page.fill('input[name="password"]', password)
            await page.click('text=Log in')
            await page.wait_for_timeout(3000)

            # Check if logged in
            print("   Checking login status...")
            await page.wait_for_url("**/home", timeout=10000)
            print("   ✓ Logged in!")

            # Click compose tweet
            print("   Opening compose box...")
            await page.click('[data-testid="SideNav_NewTweet_Button"]')
            await page.wait_for_timeout(1000)

            # Type tweet
            print(f"   Typing tweet: {text[:30]}...")
            await page.fill('[data-testid="tweetTextarea_0"]', text)
            await page.wait_for_timeout(500)

            # Click post
            print("   Posting...")
            await page.click('[data-testid="tweetButton"]')
            await page.wait_for_timeout(3000)

            print("   ✅ Tweet posted!")
            result["success"] = True
            result["timestamp"] = datetime.now().isoformat()

        except Exception as e:
            print(f"   ❌ Error: {e}")
            result["error"] = str(e)

            # Take screenshot on error
            screenshot_path = Path("twitter_error.png")
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
        "action": "twitter_post",
        "result": result
    })

    log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Post Tweet via Playwright")
    parser.add_argument("--text", required=True, help="Tweet text (max 280 chars)")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually post")
    parser.add_argument("--vault", help="Path to vault for logging")

    args = parser.parse_args()

    # Validate tweet length
    if len(args.text) > 280:
        print(f"❌ Tweet too long! {len(args.text)}/280 characters")
        sys.exit(1)

    print("=" * 50)
    print("🐦 Twitter Auto Poster")
    print("=" * 50)
    print(f"Text: {args.text}")
    print(f"Length: {len(args.text)}/280")
    print(f"Dry Run: {args.dry_run}")
    print("=" * 50)

    # Run async function
    result = asyncio.run(post_tweet(args.text, args.dry_run))

    # Log action
    log_action(result, args.vault)

    if result["success"]:
        print("\n✅ Success!")
    else:
        print(f"\n❌ Failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
