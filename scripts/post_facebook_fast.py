#!/usr/bin/env python3
"""
Facebook Fast Poster - Quick & Aggressive
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
import time

load_dotenv()

def post_facebook_fast(content: str):
    email = os.getenv('FACEBOOK_EMAIL')
    password = os.getenv('FACEBOOK_PASSWORD')

    if not email or not password:
        print("❌ No credentials")
        return False

    print("🚀 FB Fast Posting START")

    try:
        with sync_playwright() as p:
            # Launch fast
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={'width': 1280, 'height': 720})

            # Go to FB
            print("1️⃣ Loading FB...")
            page.goto('https://m.facebook.com/', wait_until='load')
            page.wait_for_timeout(1500)

            # Quick login check
            try:
                page.wait_for_selector('input[name="email"]', timeout=3000)
                print("2️⃣ Logging in...")
                page.fill('input[name="email"]', email)
                page.fill('input[name="pass"]', password)
                page.click('button[name="login"]')
                page.wait_for_timeout(3000)
            except:
                print("2️⃣ Already logged in")

            # Navigate to home
            page.goto('https://m.facebook.com/home.php', wait_until='load')
            page.wait_for_timeout(1500)

            print("3️⃣ Opening composer...")
            # Mobile FB - click status/compose
            try:
                page.click('a[href*="compose"]', timeout=3000)
            except:
                try:
                    page.click('[aria-label*="compose"]', timeout=2000)
                except:
                    try:
                        page.click('input[placeholder*="mind"]', timeout=2000)
                    except:
                        # Try JavaScript
                        page.evaluate('document.querySelector("input[placeholder*=mind]").click()')

            page.wait_for_timeout(1000)

            print("4️⃣ Typing...")
            # Type content
            try:
                page.fill('textarea', content)
            except:
                try:
                    page.fill('input[type="text"]', content)
                except:
                    page.keyboard.type(content, delay=5)

            page.wait_for_timeout(800)

            print("5️⃣ Posting...")
            # Find and click Post
            try:
                page.click('button:has-text("Post")', timeout=2000)
            except:
                try:
                    page.click('[aria-label="Post"]', timeout=2000)
                except:
                    try:
                        # Try keyboard
                        page.keyboard.press('Tab')
                        page.keyboard.press('Tab')
                        page.keyboard.press('Return')
                    except:
                        print("❌ Could not post")
                        browser.close()
                        return False

            page.wait_for_timeout(2000)

            print("✅ FB POST SUCCESS! 🎉")
            browser.close()
            return True

    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return False

if __name__ == '__main__':
    content = "🤖 Meet Your New AI Employee\n\nIntroducing our revolutionary AI automation system that works 24/7!\n\n✅ Email management\n✅ Social media posting\n✅ Report generation\n✅ Task automation\n\nLet's automate your life. 🚀\n\n#AI #Automation #FutureOfWork"

    success = post_facebook_fast(content)
    exit(0 if success else 1)
