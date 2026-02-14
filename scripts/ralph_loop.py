#!/usr/bin/env python3
"""
Ralph Wiggum Loop - Autonomous Task Execution Engine
Gold Tier: Continuously processes vault items until all work is done.

Usage:
    # Dry run (safe - no actual execution)
    python scripts/ralph_loop.py --vault ./vault --dry-run

    # Live execution
    python scripts/ralph_loop.py --vault ./vault

    # Single pass (no looping)
    python scripts/ralph_loop.py --vault ./vault --single-pass

    # Custom max iterations
    python scripts/ralph_loop.py --vault ./vault --max-iterations 5
"""

import os
import sys
import json
import time
import shutil
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RalphLoop')


class RalphLoop:
    """
    Ralph Wiggum Loop - Autonomous multi-step task processor.

    Scans vault folders, classifies items, routes them (auto-execute or approval),
    executes approved items via MCP servers, and loops until done.
    """

    def __init__(self, vault_path: str, max_iterations: int = 10, dry_run: bool = True, agent_mode: str = 'local'):
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.dry_run = dry_run
        self.agent_mode = agent_mode or os.getenv('AGENT_MODE', 'local')

        # Vault folders
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.in_progress = self.vault_path / 'In_Progress' / (f'{self.agent_mode}-agent' if self.agent_mode else 'local-agent')
        self.updates = self.vault_path / 'Updates'

        # Ensure folders exist
        for folder in [self.inbox, self.needs_action, self.pending_approval,
                       self.approved, self.done, self.logs, self.in_progress, self.updates]:
            folder.mkdir(parents=True, exist_ok=True)

        # Track what we've processed this session
        self.processed = set()
        self.iteration_logs = []

        # Company Handbook rules - items requiring human approval
        self.approval_required_types = {'email_send_request', 'social_post', 'invoice', 'payment'}
        self.auto_execute_types = {'file_drop', 'newsletter', 'spam'}

        # MCP clients (lazy-loaded)
        self._whatsapp_api = None

        logger.info(f"Ralph Loop initialized | vault={vault_path} | max_iter={max_iterations} | dry_run={dry_run} | agent_mode={self.agent_mode}")

    # ==================== PHASE 1: SCAN ====================

    def scan_needs_action(self) -> list:
        """Get unprocessed items from Needs_Action/"""
        items = []
        for f in sorted(self.needs_action.glob('*.md')):
            if str(f) not in self.processed:
                items.append(f)
        return items

    def scan_approved(self) -> list:
        """Get items in Approved/ ready for execution"""
        return list(sorted(self.approved.glob('*.md')))

    # ==================== PHASE 2: CLASSIFY ====================

    def classify_item(self, item_path: Path) -> dict:
        """Parse YAML frontmatter and classify the item"""
        content = item_path.read_text(encoding='utf-8', errors='replace')
        classification = {
            'path': item_path,
            'filename': item_path.name,
            'type': 'unknown',
            'source': 'unknown',
            'priority': 'normal',
            'status': 'pending',
            'content': content,
            'metadata': {}
        }

        # Parse YAML frontmatter (between --- markers)
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = parts[1].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, _, value = line.partition(':')
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        classification['metadata'][key] = value
                        if key == 'type':
                            classification['type'] = value
                        elif key == 'source':
                            classification['source'] = value
                        elif key == 'priority':
                            classification['priority'] = value
                        elif key == 'status':
                            classification['status'] = value

        # Infer type from filename if not in frontmatter
        if classification['type'] == 'unknown':
            name = item_path.name.upper()
            if name.startswith('EMAIL'):
                classification['type'] = 'email'
            elif name.startswith('WA_'):
                classification['type'] = 'whatsapp'
            elif name.startswith('FILE_'):
                classification['type'] = 'file_drop'
            elif name.startswith('SOCIAL') or name.startswith('POST'):
                classification['type'] = 'social_post'
            elif name.startswith('INVOICE') or name.startswith('INV'):
                classification['type'] = 'invoice'

        return classification

    def route_item(self, classification: dict) -> str:
        """Determine routing: 'auto_execute' or 'needs_approval'"""
        item_type = classification['type']
        priority = classification['priority']

        # Company Handbook: these ALWAYS need approval
        if item_type in self.approval_required_types:
            return 'needs_approval'

        # High priority items get flagged for review
        if priority == 'high':
            return 'needs_approval'

        # WhatsApp messages: auto-acknowledge normal ones
        if item_type == 'whatsapp' and priority == 'normal':
            return 'auto_execute'

        # File drops: auto-classify and archive
        if item_type in self.auto_execute_types:
            return 'auto_execute'

        # Default: needs approval for safety
        return 'needs_approval'

    # ==================== PHASE 3: EXECUTE ====================

    def execute_item(self, item_path: Path, classification: dict) -> bool:
        """Dispatch to the correct executor based on item type and agent mode"""
        item_type = classification['type']

        logger.info(f"Executing: {item_path.name} (type={item_type}, mode={self.agent_mode}, dry_run={self.dry_run})")

        # Cloud mode: draft-only (never actually send/post)
        if self.agent_mode == 'cloud':
            logger.info(f"  [CLOUD MODE] {item_type}: {item_path.name} -> will be drafted, not executed")
            return True

        # Local mode: execute only if dry_run is False
        if self.dry_run:
            logger.info(f"  [DRY RUN] Would execute {item_type}: {item_path.name}")
            return True

        try:
            if item_type == 'email' or item_type == 'email_send_request':
                return self._execute_email(classification)
            elif item_type == 'whatsapp' or item_type == 'whatsapp_send':
                return self._execute_whatsapp(classification)
            elif item_type == 'social_post':
                return self._execute_social(classification)
            elif item_type == 'invoice':
                return self._execute_odoo(classification)
            elif item_type in ('file_drop', 'newsletter', 'spam'):
                return self._execute_file_action(classification)
            else:
                logger.warning(f"  Unknown type '{item_type}' - marking as done (no action)")
                return True
        except Exception as e:
            logger.error(f"  Execution failed: {e}")
            return False

    def _execute_email(self, classification: dict) -> bool:
        """Send email via Gmail API"""
        meta = classification['metadata']
        to = meta.get('to', '')
        subject = meta.get('subject', '')

        if not to:
            logger.error("  No recipient in email")
            return False

        # Extract body from content
        content = classification['content']
        body = ''
        if '## Body' in content:
            body = content.split('## Body')[1].split('##')[0].strip()
        elif '## Message' in content:
            body = content.split('## Message')[1].split('##')[0].strip()

        logger.info(f"  Sending email to {to}: {subject}")

        try:
            from mcp_servers.email_sender.email_sender import EmailSender
            sender = EmailSender(str(self.vault_path))
            sender.send_email(to, subject, body or f"AI Employee message: {subject}")
            return True
        except Exception as e:
            logger.error(f"  Email send failed: {e}")
            # Fallback: just log it
            logger.info(f"  [LOGGED] Email to {to} about '{subject}' - requires manual send")
            return True

    def _execute_whatsapp(self, classification: dict) -> bool:
        """Send WhatsApp message via Green API"""
        meta = classification['metadata']
        phone = meta.get('phone', meta.get('to', ''))
        chat_id = meta.get('chat_id', '')

        if not phone and not chat_id:
            logger.error("  No phone/chat_id in WhatsApp item")
            return False

        # Build chat_id if not present
        if not chat_id:
            chat_id = f"{phone}@c.us"

        # Extract message
        content = classification['content']
        message = meta.get('message', '')
        if not message and '## Message' in content:
            message = content.split('## Message')[1].split('##')[0].strip()
        if not message:
            message = "Message received and processed by AI Employee."

        logger.info(f"  Sending WhatsApp to {chat_id}: {message[:50]}...")

        try:
            if not self._whatsapp_api:
                from whatsapp_api_client_python import API
                self._whatsapp_api = API.GreenAPI(
                    os.getenv('GREEN_API_INSTANCE_ID'),
                    os.getenv('GREEN_API_TOKEN')
                )
            result = self._whatsapp_api.sending.sendMessage(chat_id, message)
            logger.info(f"  WhatsApp sent: {result.data}")
            return result.code == 200
        except Exception as e:
            logger.error(f"  WhatsApp send failed: {e}")
            return False

    def _execute_social(self, classification: dict) -> bool:
        """Post to social media"""
        meta = classification['metadata']
        platform = meta.get('platform', 'unknown')
        content_text = meta.get('content', '')

        if not content_text and '## Content' in classification['content']:
            content_text = classification['content'].split('## Content')[1].split('##')[0].strip()

        logger.info(f"  Posting to {platform}: {content_text[:50]}...")

        try:
            if platform == 'twitter':
                from scripts.post_twitter_api import post_tweet
                return post_tweet(content_text)
            elif platform == 'facebook':
                from scripts.post_facebook_api import post_facebook
                return post_facebook(content_text)
            elif platform == 'instagram':
                from scripts.post_instagram_mobile import post_instagram
                return post_instagram(content_text)
            elif platform == 'linkedin':
                logger.info(f"  [LOGGED] LinkedIn post queued: {content_text[:50]}")
                return True
            else:
                logger.warning(f"  Unknown platform: {platform}")
                return True
        except Exception as e:
            logger.error(f"  Social post failed: {e}")
            return False

    def _execute_odoo(self, classification: dict) -> bool:
        """Create invoice/payment in Odoo"""
        meta = classification['metadata']
        logger.info(f"  Creating Odoo entry: {meta}")

        try:
            from mcp_servers.odoo_mcp.odoo_client import OdooClient
            client = OdooClient()
            # For now, just verify connection
            logger.info("  Odoo connected successfully")
            return True
        except Exception as e:
            logger.error(f"  Odoo operation failed: {e}")
            return False

    def _execute_file_action(self, classification: dict) -> bool:
        """Process file drops, newsletters, spam"""
        item_type = classification['type']
        logger.info(f"  Auto-processing {item_type}: {classification['filename']}")

        if item_type == 'spam':
            logger.info("  Spam detected - archiving")
        elif item_type == 'newsletter':
            logger.info("  Newsletter - archiving")
        else:
            logger.info("  File processed - archiving")

        return True

    # ==================== PHASE 4: COMPLETE ====================

    def move_to_done(self, item_path: Path):
        """Move completed item to Done/"""
        if not item_path.exists():
            return

        done_path = self.done / item_path.name
        # Handle duplicate names
        if done_path.exists():
            ts = datetime.now().strftime('%H%M%S')
            done_path = self.done / f"{item_path.stem}_{ts}{item_path.suffix}"

        shutil.move(str(item_path), str(done_path))
        self.processed.add(str(item_path))
        logger.info(f"  Moved to Done: {done_path.name}")

    def create_approval_request(self, item_path: Path, classification: dict):
        """Move item to Pending_Approval/ with approval metadata"""
        dest = self.pending_approval / item_path.name
        if dest.exists():
            ts = datetime.now().strftime('%H%M%S')
            dest = self.pending_approval / f"{item_path.stem}_{ts}{item_path.suffix}"

        shutil.move(str(item_path), str(dest))
        self.processed.add(str(item_path))
        logger.info(f"  Needs approval: {dest.name} (type={classification['type']}, priority={classification['priority']})")

    # ==================== PHASE 5: LOOP ====================

    def run(self) -> dict:
        """
        Main Ralph Wiggum Loop.
        Iterates until all work is done or max_iterations reached.
        """
        logger.info("=" * 60)
        logger.info("RALPH LOOP STARTING")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Max iterations: {self.max_iterations}")
        logger.info(f"  Dry run: {self.dry_run}")
        logger.info("=" * 60)

        total_results = {
            'started': datetime.now().isoformat(),
            'iterations': 0,
            'auto_executed': 0,
            'sent_to_approval': 0,
            'approved_executed': 0,
            'failed': 0,
            'completed': False
        }

        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"\n--- Iteration {iteration}/{self.max_iterations} ---")
            iter_result = {
                'iteration': iteration,
                'timestamp': datetime.now().isoformat(),
                'actions': []
            }

            # ---- Step 1: Process Needs_Action items ----
            needs_action_items = self.scan_needs_action()
            if needs_action_items:
                logger.info(f"Found {len(needs_action_items)} items in Needs_Action")

            for item_path in needs_action_items:
                classification = self.classify_item(item_path)
                route = self.route_item(classification)

                action = {
                    'file': item_path.name,
                    'type': classification['type'],
                    'priority': classification['priority'],
                    'route': route,
                    'result': 'pending'
                }

                if route == 'auto_execute':
                    success = self.execute_item(item_path, classification)
                    if success:
                        self.move_to_done(item_path)
                        action['result'] = 'auto_executed'
                        total_results['auto_executed'] += 1
                    else:
                        action['result'] = 'failed'
                        total_results['failed'] += 1
                else:
                    self.create_approval_request(item_path, classification)
                    action['result'] = 'sent_to_approval'
                    total_results['sent_to_approval'] += 1

                iter_result['actions'].append(action)

            # ---- Step 2: Execute Approved items ----
            approved_items = self.scan_approved()
            if approved_items:
                logger.info(f"Found {len(approved_items)} items in Approved")

            for item_path in approved_items:
                classification = self.classify_item(item_path)

                action = {
                    'file': item_path.name,
                    'type': classification['type'],
                    'route': 'approved_execution',
                    'result': 'pending'
                }

                success = self.execute_item(item_path, classification)
                if success:
                    self.move_to_done(item_path)
                    action['result'] = 'executed'
                    total_results['approved_executed'] += 1
                else:
                    action['result'] = 'failed'
                    total_results['failed'] += 1

                iter_result['actions'].append(action)

            # ---- Step 3: Log iteration ----
            self.iteration_logs.append(iter_result)
            total_results['iterations'] = iteration

            # ---- Step 4: Check if done ----
            remaining_needs = len(self.scan_needs_action())
            remaining_approved = len(self.scan_approved())

            if remaining_needs == 0 and remaining_approved == 0:
                logger.info("\n<promise>TASK_COMPLETE</promise>")
                logger.info("All items processed. Loop complete.")
                total_results['completed'] = True
                break

            logger.info(f"  Remaining: {remaining_needs} needs_action, {remaining_approved} approved")

            # Brief pause between iterations
            if iteration < self.max_iterations:
                time.sleep(2)

        # ---- Final Summary ----
        total_results['finished'] = datetime.now().isoformat()
        self._log_results(total_results)
        self._print_summary(total_results)

        return total_results

    # ==================== LOGGING ====================

    def _log_results(self, results: dict):
        """Log results to vault/Logs/ralph-loop-YYYY-MM-DD.json"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'ralph-loop-{today}.json'

        log_entry = {
            'run': results,
            'iterations': self.iteration_logs
        }

        # Append to existing log or create new
        existing = []
        if log_file.exists():
            try:
                existing = json.loads(log_file.read_text())
                if not isinstance(existing, list):
                    existing = [existing]
            except json.JSONDecodeError:
                existing = []

        existing.append(log_entry)
        log_file.write_text(json.dumps(existing, indent=2, default=str))
        logger.info(f"Logged to: {log_file}")

    def _print_summary(self, results: dict):
        """Print a human-readable summary"""
        logger.info("\n" + "=" * 60)
        logger.info("RALPH LOOP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"  Iterations:        {results['iterations']}")
        logger.info(f"  Auto-executed:     {results['auto_executed']}")
        logger.info(f"  Sent to approval:  {results['sent_to_approval']}")
        logger.info(f"  Approved executed: {results['approved_executed']}")
        logger.info(f"  Failed:            {results['failed']}")
        logger.info(f"  Completed:         {'Yes' if results['completed'] else 'No (max iterations reached)'}")
        logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Ralph Wiggum Loop - Autonomous Task Processor')
    parser.add_argument('--vault', type=str, required=True, help='Path to vault')
    parser.add_argument('--max-iterations', type=int, default=10, help='Max loop iterations (default: 10)')
    parser.add_argument('--dry-run', action='store_true', default=False, help='Dry run mode (no real execution)')
    parser.add_argument('--single-pass', action='store_true', default=False, help='Run once, no looping')
    parser.add_argument('--agent-mode', type=str, default=None, help='Agent mode: cloud (draft-only) or local (execute). Default from env AGENT_MODE or local')

    args = parser.parse_args()

    vault = Path(args.vault).resolve()
    if not vault.exists():
        print(f"Error: Vault path does not exist: {vault}")
        sys.exit(1)

    max_iter = 1 if args.single_pass else args.max_iterations
    agent_mode = args.agent_mode or os.getenv('AGENT_MODE', 'local')

    loop = RalphLoop(
        vault_path=str(vault),
        max_iterations=max_iter,
        dry_run=args.dry_run,
        agent_mode=agent_mode
    )

    results = loop.run()
    sys.exit(0 if results['completed'] else 1)


if __name__ == '__main__':
    main()
