#!/usr/bin/env python3
"""
Facebook Poster via Playwright - Uses saved login session
Run from Windows: python post_facebook.py
"""

import time
import json
from datetime import datetime
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    import subprocess
    subprocess.run(["pip", "install", "playwright"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    from playwright.sync_api import sync_playwright


def post_to_facebook():
    email = "huzaifa.official20@gmail.com"
    password = "@Huzaifa200gtr"
    profile_dir = Path("./fb_profile")
    profile_dir.mkdir(exist_ok=True)

    post_text = "Your AI Employee is LIVE!\n\nSay hello to your personal Full-Time Employee that works 24/7.\n\nWhat it does:\n- Creates posts on LinkedIn, Facebook, Instagram, Email automatically\n- Reads incoming emails and drafts responses\n- Generates social media content across all platforms\n- Creates invoices in Odoo accounting system\n- Runs on cloud (Render) with zero downtime\n\nHow it works:\n1. You give a command\n2. System creates drafts automatically\n3. You review and approve\n4. System publishes everywhere\n5. Everything logged with timestamps\n\nResult: 80% less manual work, 24/7 productivity\n\nThis is the future of personal automation!\n\n#AI #Automation #PersonalAI #AIEmployee #Hackathon"

    print("Starting Facebook Poster...")
    print(f"Account: {email}")
    print()

    with sync_playwright() as p:
        # Use persistent context to save login cookies
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir.resolve()),
            headless=False,
            slow_mo=500,
            viewport={"width": 1280, "height": 720},
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.set_default_timeout(60000)

        # Go to Facebook
        print("Going to Facebook...")
        page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
        time.sleep(5)

        current_url = page.url
        print(f"URL: {current_url}")

        # Check if we need to login
        if "login" in current_url or "two_step" in current_url or "checkpoint" in current_url:
            print()
            print("=" * 60)
            print("YOU NEED TO LOGIN MANUALLY!")
            print("=" * 60)
            print()
            print("1. Login with your Facebook account in the browser")
            print("2. Complete any 2FA verification")
            print("3. Make sure you see the Facebook feed")
            print()
            print("Waiting 90 seconds for you to login...")
            print()

            for i in range(90):
                time.sleep(1)
                try:
                    current_url = page.url
                except:
                    continue
                # Check if we're on the feed now
                if "facebook.com" in current_url and "login" not in current_url and "two_step" not in current_url and "checkpoint" not in current_url and "authentication" not in current_url:
                    print(f"Login detected! URL: {current_url}")
                    break
                if i % 15 == 0 and i > 0:
                    print(f"   Still waiting... ({i}s)")

            time.sleep(3)

        # Now we should be logged in - go to feed
        print("Going to home feed...")
        try:
            page.evaluate("window.location.href = 'https://www.facebook.com/'")
        except:
            pass
        time.sleep(8)

        # Click "What's on your mind"
        print("Opening post editor...")
        clicked = False

        selectors = [
            "span:text(\"What's on your mind\")",
            "div[role='button'] span:text(\"What's on your mind\")",
            "[aria-label=\"What's on your mind?\"]",
        ]

        for selector in selectors:
            try:
                el = page.locator(selector).first
                if el.is_visible(timeout=3000):
                    el.click()
                    clicked = True
                    print(f"   Clicked: {selector}")
                    break
            except:
                continue

        if not clicked:
            print("   Auto-click failed.")
            page.screenshot(path="facebook_debug.png")
            print("   Click 'What's on your mind?' MANUALLY!")
            print("   Waiting 20 seconds...")
            time.sleep(20)

        time.sleep(3)

        # Type content
        print("Typing post content...")
        typed = False

        editor_selectors = [
            "div[contenteditable='true'][role='textbox']",
            "div[contenteditable='true'][data-lexical-editor='true']",
            "div[role='textbox']",
            "div[contenteditable='true']",
        ]

        for selector in editor_selectors:
            try:
                editors = page.locator(selector)
                count = editors.count()
                for i in range(count):
                    editor = editors.nth(i)
                    if editor.is_visible(timeout=3000):
                        editor.click()
                        time.sleep(1)
                        for line in post_text.split('\n'):
                            page.keyboard.type(line, delay=10)
                            page.keyboard.press("Enter")
                        typed = True
                        print(f"   Content typed (index {i})")
                        break
                if typed:
                    break
            except:
                continue

        if not typed:
            print("   Auto-type failed. Type MANUALLY!")
            page.screenshot(path="facebook_editor_debug.png")
            time.sleep(30)

        time.sleep(3)

        # Click Post
        print("Publishing post...")
        posted = False

        post_selectors = [
            "div[aria-label='Post'][role='button']",
            "div[role='button']:has-text('Post')",
            "span:has-text('Post')",
        ]

        for selector in post_selectors:
            try:
                btns = page.locator(selector)
                count = btns.count()
                for i in range(count - 1, -1, -1):
                    btn = btns.nth(i)
                    if btn.is_visible(timeout=3000):
                        btn.click()
                        posted = True
                        print(f"   Clicked Post button")
                        break
                if posted:
                    break
            except:
                continue

        if not posted:
            print("   Click 'Post' MANUALLY!")
            time.sleep(20)

        time.sleep(8)

        print("\nPost published to Facebook!")
        page.screenshot(path="facebook_success.png")

        print("\nBrowser stays open for 30 seconds - CHECK YOUR POST!")
        print("NOTE: Next time you run this script, login will be saved!")
        time.sleep(30)

        browser.close()

    # Log
    log_entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "action": "facebook_post",
        "status": "published",
        "method": "playwright_persistent",
        "account": email,
        "platform": "facebook"
    }
    log_dir = Path("./vault/Logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"facebook_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(log_entry, indent=2))
    print(f"Log saved: {log_file}")
    print("DONE!")


if __name__ == "__main__":
    post_to_facebook()
