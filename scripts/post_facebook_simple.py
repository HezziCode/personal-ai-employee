#!/usr/bin/env python3
"""
Facebook Absolute Simple - Just do it
"""
import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

email = os.getenv('FACEBOOK_EMAIL')
password = os.getenv('FACEBOOK_PASSWORD')

print("🚀 Facebook Simple Post")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    # Login
    print("1. Login...")
    page.goto('https://www.facebook.com/login')
    page.fill('input[name="email"]', email)
    page.fill('input[name="pass"]', password)
    page.click('button[name="login"]')
    page.wait_for_timeout(4000)

    # Go to feed
    print("2. To feed...")
    page.goto('https://www.facebook.com')
    page.wait_for_timeout(2000)

    # Click status composer
    print("3. Compose...")
    try:
        page.click('[data-testid="status-attachment-list"]')
    except:
        try:
            page.click('input[placeholder*="mind"]')
        except:
            page.keyboard.press('c')

    page.wait_for_timeout(1000)

    # Type
    print("4. Type...")
    page.keyboard.type("🤖 AI Employee test post")

    page.wait_for_timeout(500)

    # Post
    print("5. Post...")
    page.keyboard.press('Tab')
    page.keyboard.press('Tab')
    page.keyboard.press('Return')

    page.wait_for_timeout(2000)

    print("✅ Done!")
    browser.close()
