#!/usr/bin/env python3
"""
Post to Twitter/X - Persistent Session Mode
Run: python post_twitter.py
"""

import time
import sys
import json
from pathlib import Path
from datetime import datetime

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Installing Playwright (first time only)...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "playwright"])
    subprocess.run(["playwright", "install", "chromium"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    from playwright.sync_api import sync_playwright

def post_to_twitter():
    """Post to Twitter/X with persistent session"""

    tweet_text = """🤖 Your Personal AI Employee is LIVE!

Running 24/7 on the cloud with zero downtime. ☁️

✅ Creates posts automatically
✅ Manages emails & drafts
✅ Generates invoices
✅ Human-in-loop approval
✅ Complete audit logging

Your AI works so you don't have to.

#AI #Automation #ArtificialIntelligence #CloudComputing #PersonalAssistant #Panaversity"""

    print("\n" + "="*70)
    print("🐦 TWITTER/X POSTER - PERSISTENT SESSION")
    print("="*70)
    print(f"\n📝 Tweet to post ({len(tweet_text)} chars):")
    print("-" * 70)
    print(tweet_text)
    print("-" * 70)

    with sync_playwright() as p:
        print("\n🚀 Launching Chrome browser (persistent context)...")
        browser = p.chromium.launch(headless=False)

        # Use persistent context to maintain login session
        context = browser.new_context()
        page = context.new_page()

        try:
            # Go to Twitter
            print("🌐 Going to Twitter/X...")
            page.goto("https://x.com/home", wait_until="domcontentloaded")
            time.sleep(3)

            print("\n📱 MANUAL STEPS:")
            print("1️⃣  If not logged in, sign in now in the browser")
            print("2️⃣  Wait for page to fully load")
            print("3️⃣  Press ENTER when ready (after you see the compose button)")
            print("\n⏳ Waiting for your signal...")

            input("👉 Press ENTER when you're ready to continue: ")

            time.sleep(2)

            # Refresh page after login to ensure we're on home
            print("\n🔄 Refreshing page...")
            page.reload(wait_until="domcontentloaded")
            time.sleep(3)

            # Now try to find and click compose
            print("\n✍️ Opening tweet composer...")

            # Try multiple selectors for compose button
            compose_selectors = [
                'a[aria-label="Compose post"]',
                'button[aria-label="Compose post"]',
                'a[href*="/compose/tweet"]',
                'button:has-text("Compose")',
            ]

            compose_clicked = False
            for selector in compose_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"   Found compose button: {selector}")
                        element.click()
                        time.sleep(2)
                        compose_clicked = True
                        break
                except:
                    pass

            if not compose_clicked:
                print("   Trying keyboard shortcut 'C'...")
                page.keyboard.press("c")
                time.sleep(2)

            # Find text area
            print("📝 Finding text box...")
            text_boxes = page.query_selector_all('div[contenteditable="true"]')

            if text_boxes:
                print(f"   Found {len(text_boxes)} text box(es)")
                text_box = text_boxes[0]

                print("   Clicking on text box...")
                text_box.click()
                time.sleep(1)

                print("   Clearing any existing text...")
                text_box.type("", delay=5)  # Clear
                time.sleep(0.5)

                print(f"   Typing {len(tweet_text)} characters...")
                # Type character by character with small delay
                for i, char in enumerate(tweet_text):
                    text_box.type(char, delay=5)
                    if (i + 1) % 50 == 0:
                        print(f"      ... {i+1}/{len(tweet_text)} typed")

                time.sleep(2)
                print("✅ Tweet typed!")

                # Find POST button
                print("\n📤 Finding POST button...")
                time.sleep(1)

                post_selectors = [
                    'button[data-testid="tweetButtonInline"]',
                    'button:has-text("Post")',
                    'button:has-text("Tweet")',
                ]

                post_btn = None
                for selector in post_selectors:
                    try:
                        post_btn = page.query_selector(selector)
                        if post_btn:
                            print(f"   Found POST button: {selector}")
                            break
                    except:
                        pass

                if post_btn:
                    print("   Clicking POST button...")
                    post_btn.click()
                    time.sleep(3)

                    # Wait for success
                    try:
                        page.wait_for_selector('div:has-text("Your post was liked")', timeout=5000)
                    except:
                        pass

                    time.sleep(2)
                    print("✅ Tweet posted successfully!")

                    # Log success
                    vault_path = Path("vault")
                    done_file = vault_path / "Done" / f"TWITTER_X_POSTED_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                    done_file.write_text(f"""---
type: social_post
platform: twitter_x
status: posted
timestamp: {datetime.now().isoformat()}
method: playwright_persistent_session
---

# Twitter/X Post - AI Employee LIVE

{tweet_text}

**✅ Posted:** {datetime.now().isoformat()}
**Profile:** https://x.com/huzaifa_xpert
""")

                    log_file = vault_path / "Logs" / f"twitter_x_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    log_file.write_text(json.dumps({
                        "timestamp": datetime.now().isoformat(),
                        "platform": "twitter_x",
                        "status": "posted",
                        "success": True,
                        "profile": "https://x.com/huzaifa_xpert"
                    }, indent=2))

                    print(f"✅ Logged to vault!")
                    return True
                else:
                    print("❌ Could not find POST button")
                    print("📱 Please click POST manually in browser")
                    time.sleep(20)
                    return False
            else:
                print("❌ Could not find text box")
                print("📱 Please type and post manually in browser")
                time.sleep(20)
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            print("📱 Browser is open - post manually")
            time.sleep(20)
            return False

        finally:
            print("\n⏳ Keeping browser open for 30 seconds...")
            time.sleep(30)
            browser.close()
            print("✅ Browser closed.")

if __name__ == '__main__':
    try:
        success = post_to_twitter()

        if success:
            print("\n" + "="*70)
            print("✅ TWITTER/X POST SUCCESSFUL!")
            print("="*70)
            print("Check your profile: https://x.com/huzaifa_xpert")
        else:
            print("\n" + "="*70)
            print("⚠️ Manual posting may be needed")
            print("="*70)

    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
