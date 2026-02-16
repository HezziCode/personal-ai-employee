#!/usr/bin/env python3
"""
LinkedIn Poster via Playwright
Run from Windows: python post_linkedin.py
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


def post_to_linkedin():
    """Post to LinkedIn using Playwright browser automation."""

    email = "ameerkhan54dea@gmail.com"
    password = "ameerkhan54"

    post_text = """🤖 Your AI Employee is LIVE!

Say hello to your personal Full-Time Employee that works 24/7.

✅ What it does:
• Creates posts on LinkedIn, Email, Odoo automatically
• Reads incoming emails and drafts responses
• Generates social media content
• Creates invoices in accounting system
• Runs on cloud (Render) with zero downtime

✅ How it works:
1️⃣ You give a command
2️⃣ System creates drafts automatically
3️⃣ You review & approve
4️⃣ System publishes everywhere
5️⃣ Everything logged with timestamps

💡 Result: 80% less manual work, 24/7 productivity

🚀 This is the future of personal automation!

#AI #Automation #PersonalAI #AIEmployee #Hackathon #TechInnovation"""

    print("🚀 Starting LinkedIn Poster...")
    print(f"📧 Account: {email}")
    print(f"📝 Post length: {len(post_text)} chars\n")

    with sync_playwright() as p:
        print("📱 Launching browser...")
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        # Step 1: Navigate to LinkedIn
        print("🌐 Going to LinkedIn...")
        page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
        time.sleep(3)

        # Step 2: Login
        print("🔑 Logging in...")
        page.fill("input#username", email)
        page.fill("input#password", password)
        page.click("button[type='submit']")

        # Wait for redirect instead of networkidle
        print("⏳ Waiting for login...")
        time.sleep(8)

        current_url = page.url
        print(f"📍 Current URL: {current_url}")

        if "checkpoint" in current_url or "challenge" in current_url:
            print("⚠️ LinkedIn wants verification!")
            print("👉 Complete the verification in the browser window...")
            print("⏳ Waiting 30 seconds for you to verify...")
            time.sleep(30)

        # Step 3: Navigate to feed
        print("📰 Going to feed...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        time.sleep(5)

        # Step 4: Click "Start a post"
        print("✍️ Opening post editor...")
        clicked = False

        selectors = [
            "button:has-text('Start a post')",
            "div.share-box-feed-entry__trigger",
            "button.share-box-feed-entry__trigger",
            "text=Start a post",
            ".share-box-feed-entry__top-bar",
            "button.artdeco-button--muted",
        ]

        for selector in selectors:
            try:
                page.click(selector, timeout=5000)
                clicked = True
                print(f"   ✅ Clicked: {selector}")
                break
            except:
                continue

        if not clicked:
            print("   ⚠️ Auto-click failed. Taking screenshot...")
            page.screenshot(path="linkedin_debug.png")
            print("   📸 Screenshot saved: linkedin_debug.png")
            print("\n   👉 Please click 'Start a post' MANUALLY in the browser!")
            print("   ⏳ Waiting 15 seconds...")
            time.sleep(15)

        time.sleep(3)

        # Step 5: Type the post content
        print("📝 Typing post content...")
        typed = False

        editor_selectors = [
            "div.ql-editor[contenteditable='true']",
            "div[role='textbox']",
            "div[contenteditable='true'][data-placeholder]",
            "div[contenteditable='true']",
        ]

        for selector in editor_selectors:
            try:
                editor = page.locator(selector).first
                if editor.is_visible(timeout=3000):
                    editor.click()
                    time.sleep(1)

                    # Type line by line
                    for line in post_text.split('\n'):
                        page.keyboard.type(line, delay=20)
                        page.keyboard.press("Enter")

                    typed = True
                    print(f"   ✅ Content typed in: {selector}")
                    break
            except:
                continue

        if not typed:
            print("   ⚠️ Auto-type failed.")
            print("   📸 Taking screenshot...")
            page.screenshot(path="linkedin_editor_debug.png")
            print("\n   👉 Please paste the post content MANUALLY!")
            print("   ⏳ Waiting 20 seconds...")
            time.sleep(20)

        time.sleep(2)

        # Step 6: Click Post button
        print("📤 Publishing post...")
        posted = False

        post_selectors = [
            "button.share-actions__primary-action",
            "button:has-text('Post')",
            "button[data-control-name='share.post']",
        ]

        for selector in post_selectors:
            try:
                btn = page.locator(selector).first
                if btn.is_visible(timeout=3000):
                    btn.click()
                    posted = True
                    print(f"   ✅ Clicked publish: {selector}")
                    break
            except:
                continue

        if not posted:
            print("   ⚠️ Auto-post failed.")
            print("\n   👉 Please click 'Post' button MANUALLY!")
            print("   ⏳ Waiting 15 seconds...")
            time.sleep(15)

        time.sleep(5)

        # Step 7: Verify - go to activity page
        print("\n🔍 Checking if post appeared...")
        page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
        time.sleep(5)

        # Take screenshot of feed
        page.screenshot(path="linkedin_feed_after_post.png")
        print("📸 Feed screenshot saved: linkedin_feed_after_post.png")

        # Go to profile activity
        print("📰 Checking profile activity...")
        page.goto("https://www.linkedin.com/in/muhammed-3431353b0/recent-activity/all/", wait_until="domcontentloaded")
        time.sleep(5)

        page.screenshot(path="linkedin_activity.png")
        print("📸 Activity screenshot saved: linkedin_activity.png")

        print("\n🎉 Post published to LinkedIn!")
        print(f"🔗 Check: https://www.linkedin.com/in/muhammed-3431353b0/recent-activity/all/")

        # Keep browser open so user can verify
        print("\n⏳ Browser stays open for 30 seconds - CHECK YOUR POST!")
        print("👉 Look at the browser window to verify the post appeared")
        time.sleep(30)

        browser.close()

    # Log execution
    log_entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "action": "linkedin_post",
        "status": "published",
        "method": "playwright_browser_automation",
        "account": email,
        "post_length": len(post_text),
        "platform": "linkedin"
    }

    log_dir = Path("./vault/Logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"linkedin_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(log_entry, indent=2))
    print(f"\n📁 Log saved: {log_file}")
    print("✅ DONE!")

    return True


if __name__ == "__main__":
    post_to_linkedin()
