#!/usr/bin/env python3
"""
Post directly to user's feed instead of page
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

print("📘 Facebook Direct Post (to user feed)")

content = """🤖 Meet Your New AI Employee

Introducing our revolutionary AI automation system that works 24/7 so you don't have to!

✅ Email management
✅ Social media posting
✅ Report generation
✅ Task automation

Stop wasting time on manual work. Let's automate your life. 🚀

#AI #Automation #FutureOfWork #Innovation"""

try:
    # Post to user's feed instead of page
    url = f"https://graph.facebook.com/v19.0/me/feed"

    payload = {
        'message': content,
        'access_token': token
    }

    print("📤 Posting to your feed...")
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        data = response.json()
        post_id = data.get('id', 'unknown')
        print(f"✅ Post successful!")
        print(f"📌 Post ID: {post_id}")
        print(f"🔗 View: https://www.facebook.com/{post_id}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"   Response: {response.text}")

except Exception as e:
    print(f"❌ Error: {e}")
