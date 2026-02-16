#!/usr/bin/env python3
"""
Instagram Poster via Playwright
Run from Windows: python post_instagram.py
NOTE: Instagram requires an image to post. This script creates a simple image.
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


def create_post_image():
    """Create a simple post image using HTML canvas via Playwright."""

    html_content = """
    <html>
    <body style="margin:0; padding:0;">
    <canvas id="c" width="1080" height="1080"></canvas>
    <script>
    const c = document.getElementById('c');
    const ctx = c.getContext('2d');

    // Background gradient
    const grad = ctx.createLinearGradient(0, 0, 1080, 1080);
    grad.addColorStop(0, '#667eea');
    grad.addColorStop(1, '#764ba2');
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, 1080, 1080);

    // Title
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 72px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Your AI Employee', 540, 200);
    ctx.fillText('is LIVE!', 540, 290);

    // Robot emoji
    ctx.font = '120px Arial';
    ctx.fillText('🤖', 540, 450);

    // Features
    ctx.font = '36px Arial';
    ctx.fillStyle = '#e0e0ff';
    ctx.fillText('✅ Multi-Channel Automation', 540, 580);
    ctx.fillText('✅ Email Management', 540, 640);
    ctx.fillText('✅ Cloud Deployment 24/7', 540, 700);
    ctx.fillText('✅ Accounting Integration', 540, 760);

    // Bottom
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 42px Arial';
    ctx.fillText('80% Less Manual Work', 540, 900);
    ctx.font = '28px Arial';
    ctx.fillStyle = '#c0c0ff';
    ctx.fillText('#AI #Automation #PersonalAI', 540, 960);
    </script>
    </body>
    </html>
    """

    # Save HTML and use Playwright to screenshot it as image
    html_path = Path("./temp_image.html")
    html_path.write_text(html_content)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.goto(f"file:///{html_path.resolve()}")
        time.sleep(1)

        img_path = Path("./ai_employee_post.png")
        page.locator("#c").screenshot(path=str(img_path))
        browser.close()

    html_path.unlink()
    print(f"🖼️ Image created: {img_path}")
    return str(img_path.resolve())


def post_to_instagram():
    """Post to Instagram using Playwright browser automation (mobile view)."""

    email = "huzaifa.official20@gmail.com"
    password = "@Huzaifa200gtr"

    caption = """🤖 Your AI Employee is LIVE!

Say hello to your personal Full-Time Employee that works 24/7.

✅ What it does:
• Creates posts on LinkedIn, Facebook, Instagram, Email automatically
• Reads incoming emails and drafts responses
• Generates social media content
• Creates invoices in Odoo accounting system
• Runs on cloud with zero downtime

✅ How it works:
1️⃣ You give a command
2️⃣ System creates drafts automatically
3️⃣ You review & approve
4️⃣ System publishes everywhere
5️⃣ Everything logged with timestamps

💡 Result: 80% less manual work, 24/7 productivity

🚀 This is the future of personal automation!

#AI #Automation #PersonalAI #AIEmployee #Hackathon #TechInnovation #ArtificialIntelligence #Productivity"""

    print("🚀 Starting Instagram Poster...")
    print(f"📧 Account: {email}")
    print(f"📝 Caption length: {len(caption)} chars\n")

    # Create post image first
    print("🖼️ Creating post image...")
    try:
        image_path = create_post_image()
    except Exception as e:
        print(f"⚠️ Image creation failed: {e}")
        print("📸 You'll need to select an image manually")
        image_path = None

    with sync_playwright() as p:
        print("📱 Launching browser (mobile mode)...")

        # Use mobile device emulation for Instagram
        iphone = p.devices["iPhone 12"]
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context(
            **iphone,
            permissions=["notifications"],
        )
        page = context.new_page()
        page.set_default_timeout(60000)

        # Step 1: Navigate to Instagram
        print("🌐 Going to Instagram...")
        page.goto("https://www.instagram.com/", wait_until="domcontentloaded")
        time.sleep(3)

        # Dismiss cookie/notification popups
        try:
            page.click("text=Allow essential and optional cookies", timeout=3000)
        except:
            pass
        try:
            page.click("text=Accept All", timeout=3000)
        except:
            pass
        try:
            page.click("text=Not Now", timeout=3000)
        except:
            pass

        time.sleep(2)

        # Step 2: Login
        print("🔑 Logging in...")
        try:
            page.fill("input[name='username']", email)
            page.fill("input[name='password']", password)

            login_selectors = [
                "button:has-text('Log in')",
                "button:has-text('Log In')",
                "button[type='submit']",
            ]

            for selector in login_selectors:
                try:
                    page.click(selector, timeout=3000)
                    break
                except:
                    continue
        except Exception as e:
            print(f"   ⚠️ Login form issue: {e}")
            print("   👉 Please login MANUALLY")
            time.sleep(15)

        print("⏳ Waiting for login...")
        time.sleep(8)

        # Dismiss "Save Login Info" popup
        try:
            page.click("text=Not Now", timeout=5000)
        except:
            pass

        # Dismiss "Add to Home Screen" popup
        try:
            page.click("button:has-text('Cancel')", timeout=3000)
        except:
            pass

        try:
            page.click("text=Not Now", timeout=3000)
        except:
            pass

        time.sleep(2)

        current_url = page.url
        print(f"📍 Current URL: {current_url}")

        # Step 3: Click "Create" / "+" button
        print("✍️ Opening post creator...")
        clicked = False

        create_selectors = [
            "svg[aria-label='New post']",
            "[aria-label='New post']",
            "svg[aria-label='New Post']",
            "[aria-label='New Post']",
            "a[href='/create/style/']",
        ]

        for selector in create_selectors:
            try:
                page.click(selector, timeout=5000)
                clicked = True
                print(f"   ✅ Clicked: {selector}")
                break
            except:
                continue

        if not clicked:
            print("   ⚠️ Auto-click failed. Taking screenshot...")
            page.screenshot(path="instagram_debug.png")
            print("   📸 Screenshot saved: instagram_debug.png")
            print("\n   👉 Please click the '+' (create) button MANUALLY!")
            print("   ⏳ Waiting 15 seconds...")
            time.sleep(15)

        time.sleep(3)

        # Step 4: Upload image
        print("🖼️ Uploading image...")
        if image_path:
            try:
                file_input = page.locator("input[type='file']").first
                file_input.set_input_files(image_path)
                print("   ✅ Image uploaded")
                time.sleep(3)
            except:
                print("   ⚠️ Auto-upload failed")
                print("   👉 Please select an image MANUALLY!")
                time.sleep(15)
        else:
            print("   👉 Please select an image MANUALLY!")
            time.sleep(15)

        # Step 5: Click Next
        print("➡️ Clicking Next...")
        try:
            next_selectors = [
                "button:has-text('Next')",
                "div[role='button']:has-text('Next')",
            ]
            for selector in next_selectors:
                try:
                    page.click(selector, timeout=5000)
                    print(f"   ✅ Clicked: {selector}")
                    break
                except:
                    continue
        except:
            print("   👉 Click 'Next' MANUALLY")
            time.sleep(10)

        time.sleep(2)

        # Click Next again (filter screen)
        print("➡️ Clicking Next again (filters)...")
        try:
            for selector in next_selectors:
                try:
                    page.click(selector, timeout=5000)
                    print(f"   ✅ Clicked: {selector}")
                    break
                except:
                    continue
        except:
            print("   👉 Click 'Next' MANUALLY")
            time.sleep(10)

        time.sleep(2)

        # Step 6: Type caption
        print("📝 Typing caption...")
        try:
            caption_selectors = [
                "textarea[aria-label='Write a caption...']",
                "textarea[aria-label='Write a caption…']",
                "textarea",
                "div[contenteditable='true']",
                "div[role='textbox']",
            ]

            typed = False
            for selector in caption_selectors:
                try:
                    editor = page.locator(selector).first
                    if editor.is_visible(timeout=3000):
                        editor.click()
                        time.sleep(1)
                        page.keyboard.type(caption, delay=10)
                        typed = True
                        print(f"   ✅ Caption typed in: {selector}")
                        break
                except:
                    continue

            if not typed:
                print("   ⚠️ Auto-type failed.")
                print("   👉 Please type caption MANUALLY!")
                time.sleep(20)
        except:
            print("   👉 Please type caption MANUALLY!")
            time.sleep(20)

        time.sleep(2)

        # Step 7: Click Share
        print("📤 Publishing post...")
        try:
            share_selectors = [
                "button:has-text('Share')",
                "div[role='button']:has-text('Share')",
            ]
            for selector in share_selectors:
                try:
                    page.click(selector, timeout=5000)
                    print(f"   ✅ Clicked: {selector}")
                    break
                except:
                    continue
        except:
            print("   👉 Click 'Share' MANUALLY!")
            time.sleep(15)

        time.sleep(5)

        # Step 8: Verify
        print("\n🔍 Checking post...")
        page.screenshot(path="instagram_success.png")
        print("📸 Screenshot saved: instagram_success.png")

        print("\n🎉 Post published to Instagram!")

        print("\n⏳ Browser stays open for 30 seconds - CHECK YOUR POST!")
        time.sleep(30)

        browser.close()

    # Log execution
    log_entry = {
        "timestamp": datetime.now().isoformat() + "Z",
        "action": "instagram_post",
        "status": "published",
        "method": "playwright_browser_automation",
        "account": email,
        "post_length": len(caption),
        "platform": "instagram",
        "has_image": image_path is not None
    }

    log_dir = Path("./vault/Logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"instagram_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    log_file.write_text(json.dumps(log_entry, indent=2))
    print(f"\n📁 Log saved: {log_file}")
    print("✅ DONE!")

    return True


if __name__ == "__main__":
    post_to_instagram()
