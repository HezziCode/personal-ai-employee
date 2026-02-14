"""
Claude Code Processor
Reads items from Needs_Action and uses Claude Code to process them

This is the "brain" that connects watchers to Claude Code.
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ClaudeProcessor')


class ClaudeProcessor:
    """
    Processes items using Claude Code CLI
    """

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'

        # Load company handbook rules
        self.handbook_path = self.vault_path / 'Company_Handbook.md'
        self.handbook_rules = self._load_handbook()

    def _load_handbook(self) -> str:
        """Load company handbook rules"""
        if self.handbook_path.exists():
            return self.handbook_path.read_text()
        return "No handbook found."

    def get_pending_items(self) -> list:
        """Get all unprocessed items in Needs_Action"""
        items = []
        for filepath in self.needs_action.glob('*.md'):
            content = filepath.read_text()
            # Check if not already processed
            if 'status: pending' in content:
                items.append(filepath)
        return items

    def create_prompt(self, item_path: Path) -> str:
        """Create a prompt for Claude Code"""
        content = item_path.read_text()

        prompt = f"""You are an AI Employee assistant. Process this item and take appropriate action.

## Company Rules (from Handbook):
{self.handbook_rules[:2000]}

## Item to Process:
{content}

## Your Task:
1. Analyze what action is needed
2. Determine if it requires human approval (payments >$50, new contacts, sensitive actions)
3. Create appropriate response

## Output Format:
Respond with a JSON object:
{{
    "analysis": "Brief analysis of what's needed",
    "action_type": "auto|approval_required|info_only",
    "priority": "high|normal|low",
    "suggested_response": "What to do or say",
    "approval_reason": "Why approval needed (if applicable)"
}}

Only output the JSON, nothing else."""

        return prompt

    def call_claude(self, prompt: str) -> dict:
        """Call Claude Code CLI and get response"""
        try:
            # Use claude CLI with -p flag for non-interactive print mode
            # Pass prompt as argument after -p flag
            result = subprocess.run(
                ['claude', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(self.vault_path)
            )

            if result.returncode != 0:
                logger.error(f"Claude error: {result.stderr}")
                return {"error": result.stderr}

            # Parse JSON response
            response_text = result.stdout.strip()

            # Try to extract JSON from response
            try:
                # Find JSON in response
                start = response_text.find('{')
                end = response_text.rfind('}') + 1
                if start != -1 and end > start:
                    json_str = response_text[start:end]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass

            return {"raw_response": response_text}

        except subprocess.TimeoutExpired:
            logger.error("Claude timed out")
            return {"error": "timeout"}
        except Exception as e:
            logger.error(f"Error calling Claude: {e}")
            return {"error": str(e)}

    def process_item(self, item_path: Path):
        """Process a single item"""
        logger.info(f"Processing: {item_path.name}")

        # Create prompt
        prompt = self.create_prompt(item_path)

        # Call Claude
        response = self.call_claude(prompt)

        if "error" in response:
            logger.error(f"Failed to process: {response['error']}")
            return False

        # Handle response based on action_type
        action_type = response.get('action_type', 'info_only')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        if action_type == 'approval_required':
            # Create approval request
            self._create_approval_request(item_path, response, timestamp)
        else:
            # Create plan/response
            self._create_plan(item_path, response, timestamp)

        # Update original item status
        self._update_item_status(item_path, 'processed')

        # Log the action
        self._log_action(item_path.name, response)

        return True

    def _create_approval_request(self, item_path: Path, response: dict, timestamp: str):
        """Create an approval request file"""
        content = f'''---
type: approval_request
source_item: {item_path.name}
created: {datetime.now().isoformat()}
priority: {response.get('priority', 'normal')}
status: pending_approval
---

# Approval Required

## Analysis
{response.get('analysis', 'No analysis provided')}

## Reason for Approval
{response.get('approval_reason', 'Requires human review')}

## Suggested Action
{response.get('suggested_response', 'No suggestion')}

---

## To Approve
Move this file to the `Approved` folder.

## To Reject
Move this file to the `Rejected` folder.

---
*Generated by AI Employee*
'''
        filepath = self.pending_approval / f'APPROVAL_{timestamp}_{item_path.stem}.md'
        filepath.write_text(content)
        logger.info(f"Created approval request: {filepath.name}")

    def _create_plan(self, item_path: Path, response: dict, timestamp: str):
        """Create a plan file"""
        content = f'''---
type: plan
source_item: {item_path.name}
created: {datetime.now().isoformat()}
priority: {response.get('priority', 'normal')}
action_type: {response.get('action_type', 'info_only')}
status: ready
---

# Plan: {item_path.stem}

## Analysis
{response.get('analysis', 'No analysis provided')}

## Suggested Action
{response.get('suggested_response', 'No suggestion')}

## Steps
- [ ] Review this plan
- [ ] Execute suggested action
- [ ] Mark as complete

---
*Generated by AI Employee*
'''
        filepath = self.plans / f'PLAN_{timestamp}_{item_path.stem}.md'
        filepath.write_text(content)
        logger.info(f"Created plan: {filepath.name}")

    def _update_item_status(self, item_path: Path, new_status: str):
        """Update the status in an item file"""
        content = item_path.read_text()
        content = content.replace('status: pending', f'status: {new_status}')
        item_path.write_text(content)

    def _log_action(self, item_name: str, response: dict):
        """Log the processing action"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'component': 'claude_processor',
            'item': item_name,
            'response': response
        }

        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

    def run_once(self):
        """Process all pending items once"""
        items = self.get_pending_items()
        logger.info(f"Found {len(items)} pending items")

        for item in items:
            self.process_item(item)

    def run_continuous(self, interval: int = 60):
        """Run continuously, checking for new items"""
        import time

        logger.info("Starting continuous processing...")
        logger.info(f"Check interval: {interval} seconds")

        try:
            while True:
                self.run_once()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Stopped by user")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Claude Code Processor for AI Employee')
    parser.add_argument(
        '--vault',
        type=str,
        required=True,
        help='Path to Obsidian vault'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Process once and exit (default: run continuously)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )

    args = parser.parse_args()

    vault_path = Path(args.vault)
    if not vault_path.exists():
        print(f"Error: Vault not found: {vault_path}")
        sys.exit(1)

    processor = ClaudeProcessor(str(vault_path))

    if args.once:
        processor.run_once()
    else:
        processor.run_continuous(args.interval)


if __name__ == '__main__':
    main()
