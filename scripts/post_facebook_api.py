#!/usr/bin/env python3
"""
Facebook Graph API Poster - Official API (100% Reliable)
Uses Facebook Graph API to post directly - No Playwright, No detection issues
"""
import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

def post_to_facebook_api(content: str):
    """Post to Facebook using official Graph API"""

    page_id = os.getenv('FACEBOOK_PAGE_ID')
    access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

    if not page_id or not access_token:
        print("❌ FACEBOOK_PAGE_ID or FACEBOOK_PAGE_ACCESS_TOKEN not set")
        return False

    print(f"📘 Facebook Graph API Posting")
    print(f"Page ID: {page_id}")
    print(f"Content: {content[:80]}...")

    try:
        # Facebook Graph API endpoint
        url = f"https://graph.facebook.com/v19.0/{page_id}/feed"

        # Payload
        payload = {
            'message': content,
            'access_token': access_token
        }

        print("📤 Sending to Facebook...")

        # Make POST request
        response = requests.post(url, data=payload)

        # Check response
        if response.status_code == 200:
            data = response.json()
            post_id = data.get('id', 'unknown')
            print(f"✅ Post successful!")
            print(f"📌 Post ID: {post_id}")
            print(f"🔗 View: https://www.facebook.com/{post_id}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
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

    success = post_to_facebook_api(content)
    sys.exit(0 if success else 1)
