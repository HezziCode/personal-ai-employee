#!/usr/bin/env python3
"""
Export Twitter cookies from Chrome Profile 4.
"""
import json
import sys
import shutil
import sqlite3
from pathlib import Path

STORAGE_PATH = Path(__file__).parent.parent / "vault" / ".twitter_session.json"

def main():
    chrome_cookies = Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Profile 4" / "Cookies"

    if not chrome_cookies.exists():
        print(f"Cookie file nahi mila: {chrome_cookies}")
        sys.exit(1)

    print("Chrome band hai? Cookies copy kar raha hoon...\n")

    # Copy cookies db (Chrome locks it)
    tmp_cookies = Path(__file__).parent / "_tmp_cookies.db"
    shutil.copy2(chrome_cookies, tmp_cookies)

    conn = sqlite3.connect(str(tmp_cookies))
    cursor = conn.cursor()

    # Get x.com and twitter.com cookies
    cursor.execute("""
        SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly
        FROM cookies
        WHERE host_key LIKE '%x.com' OR host_key LIKE '%twitter.com'
    """)
    rows = cursor.fetchall()
    conn.close()
    tmp_cookies.unlink()

    print(f"Found {len(rows)} cookies")

    pw_cookies = []
    for name, value, domain, path, expires, secure, httponly in rows:
        print(f"  {name} = {(value or '(encrypted)')[:30]}")
        if value:  # Only non-encrypted cookies
            pw_cookies.append({
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "expires": expires / 1000000 - 11644473600 if expires else -1,
                "httpOnly": bool(httponly),
                "secure": bool(secure),
                "sameSite": "None",
            })

    auth = [c for c in pw_cookies if c["name"] == "auth_token" and c["value"]]
    print(f"\nauth_token: {'FOUND' if auth else 'NOT FOUND (encrypted)'}")

    if not auth:
        print("\nChrome cookies encrypted hain - direct read nahi ho sakta.")
        print("\nAlternative: Manually cookie copy karo:")
        print("1. Chrome mein x.com kholo")
        print("2. F12 press karo (DevTools)")
        print("3. Application tab -> Cookies -> x.com")
        print("4. 'auth_token' ka value copy karo")
        print("5. 'ct0' ka value copy karo")
        print("6. Phir ye run karo:")
        print('   python scripts/twitter_manual_cookie.py')
        sys.exit(1)

    session = {"cookies": pw_cookies, "origins": []}
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STORAGE_PATH, "w") as f:
        json.dump(session, f)

    print(f"\nSession saved: {STORAGE_PATH}")

if __name__ == "__main__":
    main()
