#!/usr/bin/env python3
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

# Try to get page info
url = f"https://graph.facebook.com/v19.0/me"
params = {
    'access_token': token,
    'fields': 'id,name,pages{id,name}'
}

print("🔍 Getting your page info...")
response = requests.get(url, params=params)
print(response.json())
