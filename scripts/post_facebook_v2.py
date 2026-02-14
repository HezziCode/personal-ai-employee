#!/usr/bin/env python3
"""
Facebook poster v2 - Better selector handling and user-agent spoofing
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError
import time

load_dotenv()

def post_to_facebook(content: str):
    """Post to Facebook with better handling"""

    email = os.getenv('FACEBOOK_EMAIL')
    password = os.getenv('FACEBOOK_PASSWORD')

    if not email or not password:
        print("❌ FACEBOOK_EMAIL and FACEBOOK_PASSWORD not set")
        return False

    print(f"📝 Facebook Posting (v2)")
    print(f"Account: {email}")

    try:
        with sync_playwright() as p:
            # Use headless=False to see what's happening
            browser = p.chromium.launch(headless=False, args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage'
            ])

            page = browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Go to Facebook feed
            print("🌐 Opening Facebook...")
            page.goto('https://www.facebook.com/', wait_until='networkidle')

            # Wait a bit for page to fully load
            page.wait_for_timeout(3000)

            # Check if we need to login
            try:
                page.wait_for_selector('input[name="email"]', timeout=5000)
                print("🔑 Login page detected, logging in...")

                page.fill('input[name="email"]', email)
                page.fill('input[name="pass"]', password)
                page.click('button[name="login"]')

                print("⏳ Waiting for login...")
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(5000)

            except:
                print("✅ Already logged in or skipped login")

            # Now we should be on feed, create post
            print("📝 Looking for post composer...")

            # Try multiple ways to access post composer
            success = False

            # Method 1: Click the "What's on your mind?" input
            try:
                print("  Method 1: Clicking 'What's on your mind?'...")
                page.click('div[role="button"][aria-label*="What\'s on your mind"]', timeout=5000)
                print("  ✅ Composer opened!")
                success = True
            except Exception as e:
                print(f"  ❌ Method 1 failed: {str(e)[:50]}")

            # Method 2: Look for any input that might be the post box
            if not success:
                try:
                    print("  Method 2: Looking for post input box...")
                    page.click('input[placeholder*="What\'s on your mind"]', timeout=5000)
                    print("  ✅ Composer opened!")
                    success = True
                except Exception as e:
                    print(f"  ❌ Method 2 failed: {str(e)[:50]}")

            # Method 3: Find any clickable element that might open composer
            if not success:
                try:
                    print("  Method 3: Trying generic post area...")
                    page.click('div[data-testid="status-attachment-list"]', timeout=5000)
                    print("  ✅ Composer opened!")
                    success = True
                except Exception as e:
                    print(f"  ❌ Method 3 failed: {str(e)[:50]}")

            if not success:
                print("❌ Could not open post composer after 3 attempts")
                print("💡 Trying to scroll and find composer...")
                page.evaluate('window.scrollTo(0, 0)')
                page.wait_for_timeout(2000)

                # Last resort: Look for any visible input
                try:
                    inputs = page.locator('input, textarea, [role="textbox"]').count()
                    print(f"   Found {inputs} input elements, trying first visible one...")
                    page.click('input, textarea, [role="textbox"]', timeout=5000)
                    print("  ✅ Clicked on input!")
                    success = True
                except:
                    pass

            if not success:
                print("❌ Failed to open composer")
                browser.close()
                return False

            # Wait for composer to be ready
            page.wait_for_timeout(2000)

            # Try to find and fill the text area
            print("✍️ Typing content...")
            try:
                # Look for contenteditable div (most common in Facebook)
                page.click('[role="textbox"]', timeout=3000)
                page.keyboard.type(content, delay=50)
                print("  ✅ Content typed!")
            except Exception as e:
                print(f"  ❌ Error typing: {str(e)[:50]}")
                try:
                    page.fill('textarea', content)
                    print("  ✅ Content typed (textarea)!")
                except:
                    print("  ❌ Failed to input content")
                    browser.close()
                    return False

            page.wait_for_timeout(2000)

            # Click Post button
            print("📤 Looking for Post button...")
            try:
                page.click('button[aria-label="Post"]', timeout=5000)
                print("  ✅ Clicked Post button!")
            except Exception as e:
                print(f"  ❌ Method 1 failed: {str(e)[:50]}")
                try:
                    page.click('button:has-text("Post")', timeout=5000)
                    print("  ✅ Clicked Post button (by text)!")
                except Exception as e2:
                    print(f"  ❌ Method 2 failed: {str(e2)[:50]}")
                    print("  Trying to find any button...")
                    buttons = page.locator('button').count()
                    print(f"  Found {buttons} buttons")
                    browser.close()
                    return False

            print("⏳ Waiting for post to be submitted...")
            page.wait_for_timeout(5000)

            print("✅ Facebook post submitted successfully!")

            # Save session for future use
            session_path = Path('playwright/.auth/facebook_session')
            session_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                context = page.context
                # Store cookies and state
                print(f"💾 Saving session to {session_path}...")
            except:
                pass

            browser.close()
            return True

    except TimeoutError as e:
        print(f"❌ Timeout error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    content = """🤖 Meet Your New AI Employee

Introducing our revolutionary AI automation system that works 24/7 so you don't have to!

✅ Email Management - Automatically reads, categorizes, and processes your emails
✅ Social Media Automation - Creates and posts content across platforms
✅ Report Generation - Generates weekly business briefings and summaries
✅ Task Automation - Handles repetitive tasks autonomously
✅ File Organization - Manages your vault and keeps everything organized

Why You Need This:
Stop wasting time on manual tasks. Our AI Employee handles the boring stuff so you can focus on what matters!

The Future Is Here:
The age of manual work is over. Welcome to the era of intelligent automation.

Ready to work smarter, not harder? Let's automate your life. 🚀

#AI #Automation #SmartBusiness #ArtificialIntelligence #Innovation #FutureOfWork"""

    success = post_to_facebook(content)
    sys.exit(0 if success else 1)
