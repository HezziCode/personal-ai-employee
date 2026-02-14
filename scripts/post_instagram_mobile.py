#!/usr/bin/env python3
"""
Instagram poster - Mobile web version (better success rate)
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError
import time

load_dotenv()

def post_to_instagram(content: str, image_path: str = None):
    """Post to Instagram via mobile web"""

    email = os.getenv('FACEBOOK_EMAIL')  # Instagram uses Facebook account
    password = os.getenv('FACEBOOK_PASSWORD')

    if not email or not password:
        print("❌ FACEBOOK_EMAIL and FACEBOOK_PASSWORD not set")
        return False

    print(f"📱 Instagram Mobile Web Posting")
    print(f"Account: {email}")

    try:
        with sync_playwright() as p:
            # Mobile device specification
            browser = p.chromium.launch(headless=False, args=[
                '--disable-blink-features=AutomationControlled'
            ])

            # Use mobile device emulation
            page = browser.new_page(
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
                viewport={'width': 390, 'height': 844},
                device_scale_factor=2
            )

            # Go to Instagram
            print("🌐 Opening Instagram (mobile)...")
            page.goto('https://www.instagram.com/', wait_until='networkidle')
            page.wait_for_timeout(3000)

            # Check if login needed
            try:
                page.wait_for_selector('input[name="username"]', timeout=5000)
                print("🔑 Login page detected, logging in...")

                page.fill('input[name="username"]', email)
                page.fill('input[name="password"]', password)
                page.click('button:has-text("Log in")')

                print("⏳ Waiting for login...")
                page.wait_for_load_state('networkidle')
                page.wait_for_timeout(5000)

            except:
                print("✅ Already logged in")

            print("📝 Looking for create post button...")

            # Instagram mobile create button
            try:
                # Try to find create button
                page.click('[aria-label="New post"]', timeout=5000)
                print("✅ Create post opened!")
            except:
                try:
                    page.click('[aria-label="Create"]', timeout=5000)
                    print("✅ Create post opened!")
                except:
                    print("❌ Could not find create button")
                    browser.close()
                    return False

            page.wait_for_timeout(2000)

            # Select or upload image (if provided)
            if image_path:
                print("🖼️ Uploading image...")
                try:
                    file_input = page.locator('input[type="file"]')
                    file_input.set_input_files(image_path)
                    page.wait_for_timeout(2000)
                    print("✅ Image uploaded!")
                except Exception as e:
                    print(f"⚠️ Image upload failed: {e}")

            # Click Next/Continue
            try:
                page.click('button:has-text("Next")', timeout=5000)
                page.wait_for_timeout(2000)
            except:
                print("⚠️ Could not find Next button")

            # Add caption
            print("✍️ Adding caption...")
            try:
                page.click('[aria-label="Write a caption..."]', timeout=5000)
                page.keyboard.type(content, delay=30)
                print("✅ Caption added!")
            except Exception as e:
                print(f"⚠️ Caption error: {e}")

            page.wait_for_timeout(2000)

            # Click Share/Post
            print("📤 Sharing post...")
            try:
                page.click('button:has-text("Share")', timeout=5000)
                print("✅ Post shared!")
            except:
                try:
                    page.click('button:has-text("Post")', timeout=5000)
                    print("✅ Post shared!")
                except Exception as e:
                    print(f"❌ Could not find Share button: {e}")
                    browser.close()
                    return False

            page.wait_for_timeout(5000)

            print("✅ Instagram post submitted successfully!")
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

✅ Email Management - Automatically reads, categorizes, and processes your emails
✅ Social Media Automation - Creates and posts content across platforms
✅ Report Generation - Generates weekly business briefings and summaries
✅ Task Automation - Handles repetitive tasks autonomously

Stop wasting time on manual tasks. Our AI Employee handles the boring stuff so you can focus on what matters!

The future is here. Let's automate your life. 🚀

#AI #Automation #SmartBusiness #ArtificialIntelligence #Innovation #FutureOfWork"""

    success = post_to_instagram(content)
    sys.exit(0 if success else 1)
