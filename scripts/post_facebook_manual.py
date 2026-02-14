#!/usr/bin/env python3
"""
Manual Facebook poster with better error handling
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError

load_dotenv()

def post_to_facebook(content: str):
    """Post to Facebook with improved selectors"""

    email = os.getenv('FACEBOOK_EMAIL')
    password = os.getenv('FACEBOOK_PASSWORD')

    if not email or not password:
        print("❌ FACEBOOK_EMAIL and FACEBOOK_PASSWORD not set")
        return False

    print(f"📝 Posting to Facebook...")
    print(f"Content: {content[:100]}...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)  # Show browser for debugging
            page = browser.new_page()

            # Go to Facebook
            print("🌐 Opening Facebook...")
            page.goto('https://www.facebook.com/')
            page.wait_for_load_state('networkidle')

            # Check if login needed
            if 'login' in page.url or 'email' in page.url.lower():
                print("🔑 Logging in...")

                # Try multiple selectors for email field
                try:
                    page.fill('input[name="email"]', email)
                except:
                    page.fill('input#email', email)

                # Try multiple selectors for password
                try:
                    page.fill('input[name="pass"]', password)
                except:
                    page.fill('input#pass', password)

                # Click login
                try:
                    page.click('button[name="login"]')
                except:
                    page.click('button:has-text("Log in")')

                print("⏳ Waiting for login...")
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(2000)

            # Now create post
            print("📝 Creating post...")

            # Try to find and click "What's on your mind" or post composer
            try:
                # Method 1: Click the main post area
                page.click('[aria-label*="What\'s on your mind"]')
            except:
                try:
                    # Method 2: Click by text
                    page.click('text=What\'s on your mind')
                except:
                    try:
                        # Method 3: Find compose button
                        page.click('a[href*="compose"]')
                    except:
                        print("❌ Could not find post composer")
                        browser.close()
                        return False

            page.wait_for_timeout(1000)

            # Find text area and type content
            print("✍️ Typing content...")
            try:
                page.fill('[role="textbox"]', content)
            except:
                try:
                    page.fill('textarea', content)
                except:
                    print("❌ Could not find text area")
                    browser.close()
                    return False

            page.wait_for_timeout(1000)

            # Click Post button
            print("📤 Clicking Post...")
            try:
                page.click('[aria-label="Post"]')
            except:
                try:
                    page.click('button:has-text("Post")')
                except:
                    print("❌ Could not find Post button")
                    browser.close()
                    return False

            page.wait_for_timeout(3000)

            print("✅ Post submitted!")
            browser.close()
            return True

    except TimeoutError as e:
        print(f"❌ Timeout: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    content = """🤖 Meet Your New AI Employee

Introducing our revolutionary AI automation system that works 24/7 so you don't have to!

✅ Email Management - Automatically reads, categorizes, and processes your emails
✅ Social Media Automation - Creates and posts content across platforms
✅ Report Generation - Generates weekly business briefings and summaries
✅ Task Automation - Handles repetitive tasks autonomously
✅ File Organization - Manages your vault and keeps everything organized

Stop wasting time on manual tasks. Let's automate your life. 🚀

#AI #Automation #SmartBusiness #ArtificialIntelligence #Innovation #FutureOfWork"""

    post_to_facebook(content)
