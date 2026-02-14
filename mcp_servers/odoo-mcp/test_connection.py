#!/usr/bin/env python3
"""Debug Odoo connection"""

import os
import xmlrpc.client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("ODOO_URL", "http://localhost:8069")
db = os.getenv("ODOO_DB", "ai_employee")

print("=" * 50)
print("Odoo Connection Debug v2")
print("=" * 50)
print(f"URL: {url}")
print(f"Database: {db}")
print("=" * 50)

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")

# Test different username formats
test_users = [
    "admin",
    "Administrator",
    "mk26408527@gmail.com",
]

password = input("\nEnter your Odoo login password: ").strip()

print("\n" + "=" * 50)
print("Testing different username formats...")
print("=" * 50)

for username in test_users:
    print(f"\nTrying: '{username}'")
    try:
        uid = common.authenticate(db, username, password, {})
        if uid:
            print(f"   ✓ SUCCESS! UID: {uid}")
            print(f"\n   💡 USE THIS IN .env:")
            print(f"   ODOO_USERNAME={username}")
            print(f"   ODOO_API_KEY={password}")
            break
        else:
            print(f"   ✗ Failed")
    except Exception as e:
        print(f"   ✗ Error: {e}")
else:
    print("\n" + "=" * 50)
    print("All username formats failed!")
    print("=" * 50)
    print("\nCheck in Odoo browser:")
    print("1. Go to: Settings → Users & Companies → Users")
    print("2. Click on your user")
    print("3. Check 'Login' field - THAT is your username")
    print("=" * 50)
