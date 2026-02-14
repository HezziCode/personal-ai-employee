"""
Email Sender MCP Server
Sends emails via Gmail API with human-in-the-loop approval

Usage:
    # Draft mode (creates approval request):
    python email_sender.py --to recipient@email.com --subject "Subject" --body "Body" --draft

    # Send mode (after approval):
    python email_sender.py --to recipient@email.com --subject "Subject" --body "Body" --send

    # Check approved folder and send pending:
    python email_sender.py --process-approved --vault /path/to/vault
"""

import sys
import os
import argparse
import base64
import json
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Gmail API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('EmailSender')

# Gmail API scopes - need send permission
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]


class EmailSender:
    """
    Sends emails via Gmail API with human approval workflow
    """

    def __init__(self, vault_path: str, credentials_path: str = None):
        self.vault_path = Path(vault_path)
        self.credentials_path = credentials_path or Path(__file__).parent.parent.parent / 'watchers' / 'credentials.json'
        self.token_path = Path(__file__).parent / 'token_send.json'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        self.service = None
        self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API (with send permission)"""
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
                    logger.error(f"credentials.json not found at {self.credentials_path}")
                    return

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path),
                    SCOPES,
                    redirect_uri='urn:ietf:wg:oauth:2.0:oob'
                )
                # Manual auth flow for WSL
                auth_url, _ = flow.authorization_url(prompt='consent')
                print('\n=== Gmail Send Permission Required ===')
                print('Please visit this URL to authorize:')
                print(auth_url)
                print('\nAfter authorization, paste the authorization code here:')
                code = input('Enter code: ').strip()
                flow.fetch_token(code=code)
                creds = flow.credentials

            # Save token for future runs
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API authenticated (send enabled)")

    def create_draft(self, to: str, subject: str, body: str) -> Path:
        """
        Create a draft email as approval request
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_subject = "".join(c for c in subject[:30] if c.isalnum() or c in ' -_').strip().replace(' ', '_')

        filename = f'EMAIL_SEND_{timestamp}_{safe_subject}.md'
        filepath = self.pending_approval / filename

        content = f"""---
type: email_send_request
to: {to}
subject: {subject}
created: {datetime.now().isoformat()}
status: pending_approval
---

# Email Send Request

## Recipient
**To:** {to}

## Subject
{subject}

## Body
{body}

---

## Approval Instructions

**To APPROVE and SEND this email:**
Move this file to the `Approved` folder.

**To REJECT:**
Move this file to the `Rejected` folder.

---
*Created by Email Sender MCP*
"""

        filepath.write_text(content)
        logger.info(f"Draft created: {filepath}")
        return filepath

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Actually send an email via Gmail API
        """
        if not self.service:
            logger.error("Gmail service not available")
            return False

        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Encode message
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            logger.info(f"✅ Email sent! Message ID: {sent_message['id']}")

            # Log the action
            self._log_action('email_sent', {
                'to': to,
                'subject': subject,
                'message_id': sent_message['id']
            })

            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return False

    def process_approved(self):
        """
        Process all approved email requests
        """
        approved_emails = list(self.approved.glob('EMAIL_SEND_*.md'))

        if not approved_emails:
            logger.info("No approved emails to send")
            return

        for filepath in approved_emails:
            logger.info(f"Processing: {filepath.name}")

            # Parse the file
            content = filepath.read_text()

            # Extract fields from YAML frontmatter
            to = self._extract_field(content, 'to')
            subject = self._extract_field(content, 'subject')

            # Extract body from markdown
            body = self._extract_body(content)

            if not all([to, subject, body]):
                logger.error(f"Missing fields in {filepath.name}")
                continue

            # Send the email
            if self.send_email(to, subject, body):
                # Move to Done
                done_path = self.done / filepath.name
                filepath.rename(done_path)
                logger.info(f"Moved to Done: {done_path}")
            else:
                logger.error(f"Failed to send: {filepath.name}")

    def _extract_field(self, content: str, field: str) -> str:
        """Extract field from YAML frontmatter"""
        for line in content.split('\n'):
            if line.startswith(f'{field}:'):
                return line.split(':', 1)[1].strip()
        return None

    def _extract_body(self, content: str) -> str:
        """Extract email body from markdown"""
        # Find the Body section
        lines = content.split('\n')
        in_body = False
        body_lines = []

        for line in lines:
            if '## Body' in line:
                in_body = True
                continue
            if in_body:
                if line.startswith('---') or line.startswith('## '):
                    break
                body_lines.append(line)

        return '\n'.join(body_lines).strip()

    def _log_action(self, action_type: str, details: dict):
        """Log action to vault"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': 'email_sender_mcp',
            'action': action_type,
            'details': details
        }

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Email Sender MCP')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--to', help='Recipient email')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--draft', action='store_true', help='Create draft for approval')
    parser.add_argument('--send', action='store_true', help='Send directly (skip approval)')
    parser.add_argument('--process-approved', action='store_true', help='Process approved emails')

    args = parser.parse_args()

    sender = EmailSender(args.vault)

    if args.process_approved:
        sender.process_approved()
    elif args.draft:
        if not all([args.to, args.subject, args.body]):
            logger.error("--to, --subject, and --body required for draft")
            sys.exit(1)
        sender.create_draft(args.to, args.subject, args.body)
    elif args.send:
        if not all([args.to, args.subject, args.body]):
            logger.error("--to, --subject, and --body required for send")
            sys.exit(1)
        sender.send_email(args.to, args.subject, args.body)
    else:
        logger.error("Specify --draft, --send, or --process-approved")
        sys.exit(1)


if __name__ == '__main__':
    main()
