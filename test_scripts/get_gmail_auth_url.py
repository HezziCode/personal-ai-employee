#!/usr/bin/env python3
"""
Generate Gmail OAuth URL for manual authentication.
Open the URL in your browser, authorize, and copy the code back.
"""

import json
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly'
]

def get_auth_url():
    """Generate OAuth URL for manual authentication."""

    credentials_path = Path('./watchers/credentials.json')

    if not credentials_path.exists():
        print("❌ credentials.json not found!")
        return

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_path),
            scopes=SCOPES
        )

        # Generate auth URL
        auth_url, state = flow.authorization_url(prompt='consent')

        print("\n" + "="*80)
        print("🔐 GMAIL OAUTH AUTHENTICATION")
        print("="*80)
        print("\n📍 Scopes requested: SEND + READ emails\n")
        print("🔗 Copy this URL to your browser:")
        print(f"\n{auth_url}\n")
        print("="*80)
        print("\n1. Open the URL in your browser")
        print("2. Click 'Allow' to grant permissions")
        print("3. Copy the authorization code from the redirect URL")
        print("4. Paste it below and press Enter\n")

        auth_code = input("📋 Enter authorization code: ").strip()

        if not auth_code:
            print("❌ No code provided!")
            return

        # Exchange code for token
        creds = flow.fetch_token(code=auth_code)

        # Save token
        token_path = Path('./watchers/token.json')
        token_data = {
            'token': creds.get('access_token'),
            'refresh_token': creds.get('refresh_token'),
            'token_uri': 'https://oauth2.googleapis.com/token',
            'client_id': json.loads(credentials_path.read_text())['installed']['client_id'],
            'client_secret': json.loads(credentials_path.read_text())['installed']['client_secret'],
            'scopes': SCOPES,
            'expiry': creds.get('expires_in')
        }

        token_path.write_text(json.dumps(token_data, indent=2))

        print("\n✅ Token saved successfully!")
        print(f"📁 Location: {token_path}")
        print("✨ Gmail is now ready to send emails!\n")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    get_auth_url()
