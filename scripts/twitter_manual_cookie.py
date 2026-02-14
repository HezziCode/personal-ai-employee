#!/usr/bin/env python3
"""
Manually enter Twitter cookies from browser DevTools.
"""
import json
import sys
from pathlib import Path

STORAGE_PATH = Path(__file__).parent.parent / "vault" / ".twitter_session.json"

def main():
    print("=" * 50)
    print("TWITTER MANUAL COOKIE ENTRY")
    print("=" * 50)
    print()
    print("Chrome mein x.com kholo, F12 press karo")
    print("Application tab -> Cookies -> https://x.com")
    print("Neeche 2 values copy karo:\n")

    auth_token = input("auth_token value paste karo: ").strip()
    ct0 = input("ct0 value paste karo: ").strip()

    if not auth_token or not ct0:
        print("Dono values chahiye!")
        sys.exit(1)

    cookies = [
        {"name": "auth_token", "value": auth_token, "domain": ".x.com", "path": "/", "expires": -1, "httpOnly": True, "secure": True, "sameSite": "None"},
        {"name": "ct0", "value": ct0, "domain": ".x.com", "path": "/", "expires": -1, "httpOnly": False, "secure": True, "sameSite": "Lax"},
    ]

    session = {"cookies": cookies, "origins": []}
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w") as f:
        json.dump(session, f)

    print(f"\nSession saved: {STORAGE_PATH}")
    print("Ab WSL se post kar sakte ho!")

if __name__ == "__main__":
    main()
