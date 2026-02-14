#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

print("🔍 Finding all pages you manage...\n")

# Method 1: Get accounts (pages) connected to this token
url = f"https://graph.facebook.com/v19.0/me/accounts"
params = {'access_token': token}

response = requests.get(url, params=params)
data = response.json()

if 'data' in data and len(data['data']) > 0:
    print("✅ Found pages:\n")
    for page in data['data']:
        print(f"📄 Page Name: {page.get('name')}")
        print(f"   Page ID: {page.get('id')}")
        print(f"   Category: {page.get('category')}")
        print()
else:
    print(f"❌ No pages found or error:")
    print(data)
