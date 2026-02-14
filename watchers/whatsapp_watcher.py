"""
WhatsApp Watcher
Monitors WhatsApp for new incoming messages via Green API and creates action items

Setup required:
1. Create a free account at https://green-api.com
2. Create an instance and scan the QR code with your WhatsApp
3. Copy Instance ID and API Token to .env file
4. Run this script: python whatsapp_watcher.py --vault ../vault
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Green API imports
try:
    from whatsapp_api_client_python import API
    GREENAPI_AVAILABLE = True
except ImportError:
    GREENAPI_AVAILABLE = False
    print("Green API not installed. Run: pip install whatsapp-api-client-python")

from dotenv import load_dotenv

load_dotenv()


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp for new incoming messages via Green API
    Creates action items in Needs_Action folder
    """

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=5)  # Check every 5 seconds

        self.instance_id = os.getenv("GREEN_API_INSTANCE_ID")
        self.api_token = os.getenv("GREEN_API_TOKEN")
        self.processed_ids = set()
        self.greenAPI = None

        # Priority keywords from Company Handbook
        self.priority_keywords = ['urgent', 'asap', 'emergency', 'deadline', 'important']
        self.invoice_keywords = ['invoice', 'payment', 'bill', 'receipt', 'pay']
        self.meeting_keywords = ['meeting', 'call', 'schedule', 'calendar', 'zoom']
        self.support_keywords = ['help', 'issue', 'problem', 'broken', 'error', 'bug']

        # Auto-reply messages from Company Handbook
        self.business_hours_reply = "Thank you for your message. I'll respond shortly."
        self.after_hours_reply = "I'll get back to you tomorrow morning."

        if not self.instance_id or not self.api_token:
            self.logger.error("GREEN_API_INSTANCE_ID and GREEN_API_TOKEN required in .env")
            self.logger.error("Sign up at https://green-api.com and create an instance")
            return

        if GREENAPI_AVAILABLE:
            self._connect()

    def _connect(self):
        """Connect to Green API"""
        try:
            self.greenAPI = API.GreenAPI(self.instance_id, self.api_token)
            self.logger.info("Green API connected successfully")
        except Exception as e:
            self.logger.error(f"Green API connection failed: {e}")

    def _is_business_hours(self) -> bool:
        """Check if current time is within business hours (9 AM - 9 PM)"""
        hour = datetime.now().hour
        return 9 <= hour < 21

    def check_for_updates(self) -> list:
        """Poll Green API for new incoming messages - drains entire queue"""
        if not self.greenAPI:
            self.logger.warning("Green API not available")
            return []

        messages = []

        try:
            # Drain all pending notifications from the queue
            while True:
                self.logger.debug("Polling Green API...")
                response = self.greenAPI.receiving.receiveNotification()

                # No more notifications in queue
                if response.code != 200 or response.data is None:
                    break

                receipt_id = response.data.get("receiptId")
                body = response.data.get("body", {})
                webhook_type = body.get("typeWebhook", "")

                # Only process incoming text messages
                if webhook_type == "incomingMessageReceived":
                    message_data = body.get("messageData", {})
                    type_message = message_data.get("typeMessage", "")

                    if type_message == "textMessage":
                        message_id = body.get("idMessage", "")

                        if message_id not in self.processed_ids:
                            sender_data = body.get("senderData", {})
                            text = message_data.get("textMessageData", {}).get("textMessage", "")

                            messages.append({
                                "receipt_id": receipt_id,
                                "message_id": message_id,
                                "sender_name": sender_data.get("senderName", "Unknown"),
                                "sender_contact_name": sender_data.get("senderContactName", ""),
                                "phone": sender_data.get("sender", "").replace("@c.us", ""),
                                "chat_id": sender_data.get("chatId", ""),
                                "text": text,
                                "timestamp": body.get("timestamp", 0)
                            })
                        else:
                            self.greenAPI.receiving.deleteNotification(receipt_id)
                    else:
                        # Non-text message (image, audio, etc.) - skip
                        self.greenAPI.receiving.deleteNotification(receipt_id)
                else:
                    # Non-message notification (status, ack, etc.) - skip
                    self.greenAPI.receiving.deleteNotification(receipt_id)

        except Exception as e:
            self.logger.error(f"Error polling Green API: {e}")

        return messages

    def _determine_priority(self, text: str) -> str:
        """Determine message priority based on Company Handbook keywords"""
        text_lower = text.lower()

        if any(kw in text_lower for kw in self.priority_keywords):
            return 'high'
        if any(kw in text_lower for kw in self.invoice_keywords):
            return 'high'
        return 'normal'

    def _determine_category(self, text: str) -> str:
        """Categorize message based on content"""
        text_lower = text.lower()

        if any(kw in text_lower for kw in self.invoice_keywords):
            return 'invoice'
        if any(kw in text_lower for kw in self.meeting_keywords):
            return 'meeting'
        if any(kw in text_lower for kw in self.support_keywords):
            return 'support'
        return 'general'

    def _send_auto_reply(self, chat_id: str):
        """Send auto-reply based on business hours"""
        if not self.greenAPI:
            return

        try:
            reply = self.business_hours_reply if self._is_business_hours() else self.after_hours_reply
            self.greenAPI.sending.sendMessage(chat_id, reply)
            self.logger.info(f"Auto-reply sent to {chat_id}")
        except Exception as e:
            self.logger.error(f"Failed to send auto-reply: {e}")

    def create_action_file(self, message: dict) -> Path:
        """Create an action file for a WhatsApp message"""
        priority = self._determine_priority(message['text'])
        category = self._determine_category(message['text'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Display name: prefer contact name, fallback to sender name
        display_name = message.get('sender_contact_name') or message['sender_name']

        content = f'''---
type: whatsapp
source: whatsapp
message_id: {message['message_id']}
sender: {display_name}
phone: {message['phone']}
chat_id: {message['chat_id']}
received: {datetime.now().isoformat()}
category: {category}
priority: {priority}
status: pending
---

# WhatsApp: {display_name}

## From
**{display_name}** (+{message['phone']})

## Message
{message['text']}

---

## Suggested Actions

- [ ] Read and understand message
- [ ] Reply to sender
- [ ] Create task if needed
- [ ] Archive after processing

## Notes

Add any notes here after processing.

---
*Created by WhatsApp Watcher*
'''

        # Create safe filename
        safe_name = "".join(c for c in display_name[:20] if c.isalnum() or c in ' -_').strip()
        safe_name = safe_name.replace(' ', '_') or 'Unknown'
        action_filename = f'WA_{timestamp}_{safe_name}.md'
        action_path = self.needs_action / action_filename
        action_path.write_text(content)

        # Mark as processed
        self.processed_ids.add(message['message_id'])

        # Delete the notification from Green API queue
        try:
            self.greenAPI.receiving.deleteNotification(message['receipt_id'])
        except Exception as e:
            self.logger.error(f"Failed to delete notification: {e}")

        # Send auto-reply
        self._send_auto_reply(message['chat_id'])

        # Log the action
        self.log_action('whatsapp_detected', {
            'message_id': message['message_id'],
            'sender': display_name,
            'phone': message['phone'],
            'category': category,
            'priority': priority,
            'preview': message['text'][:100]
        })

        self.logger.info(f'Created action: {action_filename}')
        return action_path


def main():
    """Main entry point"""
    import argparse

    if not GREENAPI_AVAILABLE:
        print("Please install Green API dependency:")
        print("pip install whatsapp-api-client-python")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument(
        '--vault',
        type=str,
        default='../vault',
        help='Path to Obsidian vault (default: ../vault)'
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

    # Check env vars
    if not os.getenv("GREEN_API_INSTANCE_ID") or not os.getenv("GREEN_API_TOKEN"):
        print("\nSetup Required:")
        print("1. Create a free account at https://green-api.com")
        print("2. Create an instance and scan the QR code with your WhatsApp")
        print("3. Add to your .env file:")
        print("   GREEN_API_INSTANCE_ID=your_instance_id")
        print("   GREEN_API_TOKEN=your_api_token")
        sys.exit(1)

    watcher = WhatsAppWatcher(str(vault_path))
    watcher.run()


if __name__ == '__main__':
    main()
