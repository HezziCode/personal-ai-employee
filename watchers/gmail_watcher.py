"""
Gmail Watcher
Monitors Gmail for new important/unread emails and creates action items

Setup required:
1. Create a Google Cloud project
2. Enable Gmail API
3. Create OAuth credentials
4. Download credentials.json to this folder
5. Run this script - it will open browser for authentication
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import base64
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Gmail API imports (install with: pip install google-api-python-client google-auth-oauthlib)
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API not installed. Run: pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for new unread/important emails
    Creates action items in Needs_Action folder
    """

    def __init__(self, vault_path: str, credentials_path: str = None):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes

        self.credentials_path = credentials_path or Path(__file__).parent / 'credentials.json'
        self.token_path = Path(__file__).parent / 'token.json'
        self.processed_ids = set()
        self.service = None

        # Priority keywords from Company Handbook
        self.priority_keywords = ['urgent', 'asap', 'important', 'deadline', 'emergency']
        self.invoice_keywords = ['invoice', 'payment', 'bill', 'receipt']

        if GMAIL_AVAILABLE:
            self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not Path(self.credentials_path).exists():
                    self.logger.error(f"credentials.json not found at {self.credentials_path}")
                    self.logger.error("Please download OAuth credentials from Google Cloud Console")
                    return

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path),
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                # Manual auth flow for WSL
                auth_url, _ = flow.authorization_url(prompt='consent')
                print('\nPlease visit this URL to authorize:')
                print(auth_url)
                print('\nAfter authorization, paste the authorization code here:')
                code = input('Enter code: ').strip()
                flow.fetch_token(code=code)
                creds = flow.credentials

            # Save token for future runs
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API authenticated successfully")

    def check_for_updates(self) -> list:
        """Check for new unread important emails"""
        if not self.service:
            self.logger.warning("Gmail service not available")
            return []

        try:
            # Query for unread important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking Gmail: {e}")
            return []

    def _get_email_details(self, message_id: str) -> dict:
        """Get full email details"""
        msg = self.service.users().messages().get(
            userId='me',
            id=message_id,
            format='full'
        ).execute()

        # Extract headers
        headers = {}
        for header in msg['payload']['headers']:
            headers[header['name'].lower()] = header['value']

        # Get body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')

        return {
            'id': message_id,
            'from': headers.get('from', 'Unknown'),
            'to': headers.get('to', ''),
            'subject': headers.get('subject', 'No Subject'),
            'date': headers.get('date', ''),
            'snippet': msg.get('snippet', ''),
            'body': body[:1000]  # Limit body length
        }

    def _determine_priority(self, email: dict) -> str:
        """Determine email priority based on keywords"""
        text = f"{email['subject']} {email['snippet']}".lower()

        if any(kw in text for kw in self.priority_keywords):
            return 'high'
        if any(kw in text for kw in self.invoice_keywords):
            return 'high'
        return 'normal'

    def _determine_category(self, email: dict) -> str:
        """Categorize email based on content"""
        text = f"{email['subject']} {email['snippet']}".lower()

        if any(kw in text for kw in self.invoice_keywords):
            return 'invoice'
        if 'meeting' in text or 'calendar' in text:
            return 'meeting'
        if 'newsletter' in text or 'unsubscribe' in text:
            return 'newsletter'
        return 'general'

    def create_action_file(self, message) -> Path:
        """Create an action file for an email"""
        email = self._get_email_details(message['id'])

        priority = self._determine_priority(email)
        category = self._determine_category(email)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        content = f'''---
type: email
source: gmail
message_id: {email['id']}
from: {email['from']}
subject: {email['subject']}
received: {email['date']}
category: {category}
priority: {priority}
status: pending
---

# Email: {email['subject']}

## From
{email['from']}

## Preview
{email['snippet']}

## Full Content
{email['body']}

---

## Suggested Actions

- [ ] Read full email
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes

Add any notes here after processing.

---
*Created by Gmail Watcher*
'''

        # Create safe filename
        safe_subject = "".join(c for c in email['subject'][:30] if c.isalnum() or c in ' -_').strip()
        action_filename = f'EMAIL_{timestamp}_{safe_subject}.md'
        action_path = self.needs_action / action_filename
        action_path.write_text(content)

        # Mark as processed
        self.processed_ids.add(message['id'])

        # Log the action
        self.log_action('email_detected', {
            'message_id': email['id'],
            'from': email['from'],
            'subject': email['subject'],
            'category': category,
            'priority': priority
        })

        self.logger.info(f'Created action: {action_filename}')
        return action_path


def main():
    """Main entry point"""
    import argparse

    if not GMAIL_AVAILABLE:
        print("Please install Gmail API dependencies:")
        print("pip install google-api-python-client google-auth-oauthlib google-auth-httplib2")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Gmail Watcher for AI Employee')
    parser.add_argument(
        '--vault',
        type=str,
        default='../vault',
        help='Path to Obsidian vault (default: ../vault)'
    )
    parser.add_argument(
        '--credentials',
        type=str,
        default=None,
        help='Path to Google OAuth credentials.json'
    )

    args = parser.parse_args()

    # Resolve vault path
    vault_path = Path(args.vault)
    if not vault_path.is_absolute():
        vault_path = Path(__file__).parent / args.vault
    vault_path = vault_path.resolve()

    print(f"Vault path: {vault_path}")

    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)

    watcher = GmailWatcher(str(vault_path), args.credentials)
    watcher.run()


if __name__ == '__main__':
    main()
