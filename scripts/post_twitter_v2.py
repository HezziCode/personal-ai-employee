#!/usr/bin/env python3
"""
Twitter poster v2 - Improved selectors and handling
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError
import time

load_dotenv()

def post_to_twitter(content: str):
    """Post to Twitter with improved selectors"""

    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')

    if not email or not password:
        print("❌ TWITTER_EMAIL and TWITTER_PASSWORD not set")
        return False

    print(f"🐦 Twitter Posting (v2)")
    print(f"Account: {email}")
    print(f"Content: {content[:80]}...")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                '--disable-blink-features=AutomationControlled'
            ])

            page = browser.new_page(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            # Go to Twitter
            print("🌐 Opening Twitter...")
            page.goto('https://twitter.com/home', wait_until='networkidle')
            page.wait_for_timeout(3000)

            # Check if login needed
            try:
                page.wait_for_selector('input[autocomplete="username"]', timeout=8000)
                print("🔑 Login detected, logging in...")

                page.fill('input[autocomplete="username"]', email)
                page.click('text=Next')
                page.wait_for_selector('input[type="password"]', timeout=10000)

                page.fill('input[type="password"]', password)
                page.click('text=Log in')

                print("⏳ Waiting for home feed...")
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(5000)

            except TimeoutError:
                print("✅ Already logged in or login skipped")
            except Exception as e:
                print(f"⚠️ Login issue: {e}")

            # Now compose tweet
            print("✍️ Looking for compose button...")

            # Try to find and click compose
            try:
                # Method 1: Click the compose button (usually on sidebar)
                page.click('a[href="/compose/tweet"]', timeout=5000)
                print("  ✅ Clicked compose button!")
            except:
                try:
                    # Method 2: Try the new tweet button
                    page.click('[role="button"][aria-label*="Post"]', timeout=5000)
                    print("  ✅ Clicked post button!")
                except:
                    try:
                        # Method 3: Look for any compose button
                        page.click('button:has-text("Post")', timeout=5000)
                        print("  ✅ Clicked post button (text)!")
                    except:
                        try:
                            # Method 4: Press 'c' hotkey to compose
                            page.keyboard.press('c')
                            page.wait_for_timeout(1000)
                            print("  ✅ Opened compose with hotkey!")
                        except Exception as e:
                            print(f"  ❌ Could not open compose: {e}")
                            browser.close()
                            return False

            page.wait_for_timeout(2000)

            # Find and fill tweet text box
            print("📝 Typing tweet...")
            try:
                # Try multiple ways to find text input
                try:
                    # Method 1: Click textbox then type
                    page.click('[role="textbox"]', timeout=3000)
                    page.wait_for_timeout(500)
                    page.keyboard.type(content, delay=10)
                    print("  ✅ Tweet text entered (textbox)!")
                except:
                    # Method 2: Type directly (focus already on input)
                    page.keyboard.type(content, delay=10)
                    print("  ✅ Tweet text entered (direct)!")
            except Exception as e:
                print(f"  ❌ Error entering text: {e}")
                browser.close()
                return False

            page.wait_for_timeout(1000)

            # Find and click the Post/Tweet button
            print("📤 Posting tweet...")
            success = False

            try:
                # Method 1: Use Tab to navigate to Post button and Enter
                page.keyboard.press('Tab')
                page.wait_for_timeout(200)
                page.keyboard.press('Return')
                print("  ✅ Posted with Tab+Enter!")
                success = True
            except Exception as e1:
                print(f"  Method 1 failed: {str(e1)[:30]}")
                try:
                    # Method 2: Ctrl+Enter keyboard shortcut
                    page.keyboard.press('Control+Enter')
                    print("  ✅ Posted with Ctrl+Enter!")
                    success = True
                except Exception as e2:
                    print(f"  Method 2 failed: {str(e2)[:30]}")
                    try:
                        # Method 3: Meta+Enter (Windows)
                        page.keyboard.press('Meta+Enter')
                        print("  ✅ Posted with Meta+Enter!")
                        success = True
                    except Exception as e3:
                        print(f"  Method 3 failed: {str(e3)[:30]}")
                        try:
                            # Method 4: Find and click Post text in any button
                            page.evaluate('document.querySelector("button:contains(\'Post\')").click()')
                            print("  ✅ Posted with JS click!")
                            success = True
                        except:
                            print(f"  ❌ Could not post")

            if not success:
                browser.close()
                return False

            print("⏳ Waiting for tweet to be posted...")
            page.wait_for_timeout(5000)

            print("✅ Tweet posted successfully! 🎉")

            browser.close()
            return True

    except TimeoutError as e:
        print(f"❌ Timeout: {e}")
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
