#!/usr/bin/env python3
"""
Post to Twitter using saved session cookies (headless).
Usage: python twitter_post.py --content "Your tweet text" [--dry-run]
"""
import asyncio
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

STORAGE_PATH = Path(__file__).parent.parent / "vault" / ".twitter_session.json"
LOGS_PATH = Path(__file__).parent.parent / "vault" / "Logs"


def log_action(result: dict):
    LOGS_PATH.mkdir(parents=True, exist_ok=True)
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": "social_media_post",
        "platform": "twitter",
        "actor": "claude_code",
        "result": "success" if result.get("success") else "failure",
        "details": result
    }
    log_file = LOGS_PATH / f"social_media_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


async def post_tweet(content: str, dry_run: bool = False) -> dict:
    if not STORAGE_PATH.exists():
        return {"success": False, "error": "No saved session. Export cookies first."}

    if dry_run:
        print(f"[DRY RUN] Would tweet: {content[:100]}...")
        return {"success": True, "dry_run": True, "platform": "twitter"}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            storage_state=str(STORAGE_PATH),
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = await context.new_page()

        try:
            await page.goto('https://x.com/home', timeout=20000)
            await asyncio.sleep(4)

            if 'login' in page.url:
                await browser.close()
                return {"success": False, "error": "Session expired. Export cookies again."}

            # Nuke ALL overlays
            await page.evaluate("""() => {
                const layers = document.getElementById('layers');
                if (layers) layers.innerHTML = '';
            }""")
            await asyncio.sleep(2)

            # Click on tweet box using force
            tweet_box = page.locator('[data-testid="tweetTextarea_0"]').first
            await tweet_box.click(force=True)
            await asyncio.sleep(1)

            # Type content
            await page.keyboard.type(content, delay=20)
            await asyncio.sleep(2)

            # Click post button with force
            post_btn = page.locator('[data-testid="tweetButtonInline"]').first
            await post_btn.click(force=True)
            await asyncio.sleep(5)

            result = {
                "success": True,
                "platform": "twitter",
                "content": content[:100],
                "url": "https://x.com/huzaifa_xpert"
            }
            log_action(result)
            await browser.close()
            return result

        except Exception as e:
            await browser.close()
            result = {"success": False, "platform": "twitter", "error": str(e)}
            log_action(result)
            return result


def main():
    parser = argparse.ArgumentParser(description='Twitter Poster (Saved Session)')
    parser.add_argument('--content', required=True, help='Tweet content')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    result = asyncio.run(post_tweet(args.content, dry_run=args.dry_run))
    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
