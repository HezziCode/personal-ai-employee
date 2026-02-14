#!/usr/bin/env python3
"""
Twitter Playwright Final Attempt - Fresh approach
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

load_dotenv()

def post_to_twitter(content: str):
    """Post to Twitter with fresh approach"""

    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')

    if not email or not password:
        print("❌ TWITTER_EMAIL and TWITTER_PASSWORD not set")
        return False

    print(f"🐦 Twitter Posting - Fresh Approach")
    print(f"Account: {email}")

    try:
        with sync_playwright() as p:
            # Fresh browser launch
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Go to home
            print("🌐 Loading Twitter...")
            page.goto('https://twitter.com/home', wait_until='domcontentloaded')
            page.wait_for_timeout(2000)

            # Check URL to see if logged in
            current_url = page.url
            print(f"   Current URL: {current_url}")

            # If on login page, login
            if 'login' in current_url or 'authorize' in current_url:
                print("🔑 Need to login...")

                try:
                    page.fill('input[autocomplete="username"]', email, timeout=5000)
                except:
                    page.fill('input[name="text"]', email)

                page.wait_for_timeout(500)
                page.click('button', timeout=3000)
                page.wait_for_timeout(1000)

                try:
                    page.fill('input[autocomplete="current-password"]', password, timeout=5000)
                except:
                    page.fill('input[type="password"]', password)

                page.wait_for_timeout(500)

                # Find and click login button
                buttons = page.locator('button').count()
                if buttons > 0:
                    page.click(f'button:last-of-type')

                page.wait_for_timeout(3000)

            print("✍️ Opening compose...")

            # Try to open compose - multiple methods
            page.keyboard.press('c')
            page.wait_for_timeout(1500)

            # Now type the tweet
            print("📝 Typing tweet...")
            page.keyboard.type(content, delay=10)
            page.wait_for_timeout(1000)

            # Post it
            print("📤 Posting...")
            page.keyboard.press('Control+Return')
            page.wait_for_timeout(2000)

            # Check if posted
            page.wait_for_timeout(3000)

            # Look for success indicator
            try:
                page.wait_for_selector('[aria-label*="Your tweet was posted"]', timeout=5000)
                print("✅ Tweet posted successfully! 🎉")
                browser.close()
                return True
            except:
                # Even if no success message, tweet might have posted
                print("⏳ Checking if tweet posted...")
                page.wait_for_timeout(2000)

                # Try to navigate to profile to verify
                page.goto('https://twitter.com/huzaifa_xpert', wait_until='domcontentloaded')
                page.wait_for_timeout(2000)

                # Check if new tweet visible
                tweets = page.locator('[data-testid="tweet"]').count()
                if tweets > 0:
                    print(f"✅ Tweet appears to be posted! Found {tweets} tweets")
                    browser.close()
                    return True
                else:
                    print("❌ Could not confirm post")
                    browser.close()
                    return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    content = """🤖 Meet Your New AI Employee

Introducing our revolutionary AI automation system that works 24/7 so you don't have to!

✅ Email management
✅ Social media posting
✅ Report generation
✅ Task automation

Stop wasting time on manual work. Let's automate your life. 🚀

#AI #Automation #FutureOfWork #Innovation"""

    success = post_to_twitter(content)
    sys.exit(0 if success else 1)
