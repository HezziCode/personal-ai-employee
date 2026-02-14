#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

access_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

url = f"https://graph.facebook.com/v19.0/me/accounts"
params = {'access_token': access_token}

print("🔍 Looking for pages...")
response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print("\n📋 Pages found:")
    for page in data.get('data', []):
        print(f"Name: {page.get('name')}")
        print(f"ID: {page.get('id')}")
        print()
else:
    print(f"Error: {response.text}")
