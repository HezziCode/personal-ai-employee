#!/usr/bin/env python3
"""
Social Media Draft Watcher
Monitors Social_Media/*_Drafts/ folders and creates approval requests

Usage:
    python social_media_watcher.py --vault /path/to/vault
"""

import sys
import time
import argparse
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SocialMediaWatcher')


class DraftApprovalHandler(FileSystemEventHandler):
    """Handles new draft files and creates approval requests"""

    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.social_media = self.vault / 'Social_Media'
        self.approved = self.social_media / 'Approved'
        self.processed = set()
        self.approved.mkdir(parents=True, exist_ok=True)

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return

        file_path = Path(event.src_path)

        # Avoid duplicate processing
        if file_path in self.processed:
            return

        self.processed.add(file_path)
        time.sleep(0.5)  # Wait for file to be fully written

        # Determine platform from folder name
        parent_name = file_path.parent.name
        platform = parent_name.replace('_Drafts', '').lower()

        if platform not in ['twitter', 'facebook', 'instagram', 'linkedin']:
            logger.warning(f"⚠️ Unknown platform folder: {parent_name}")
            return

        # Create approval request
        self._create_approval(file_path, platform)

    def _create_approval(self, draft_file: Path, platform: str):
        """Create approval request in Approved folder"""
        try:
            # Read draft
            content = draft_file.read_text(encoding='utf-8')

            # Create approval file
            approval_name = f"{platform.upper()}_{draft_file.stem}_approval.md"
            approval_file = self.approved / approval_name

            # Add approval header
            approval_content = f"""---
platform: {platform}
status: pending_approval
created: {datetime.now().isoformat()}
original_draft: {draft_file.name}
---

# {platform.title()} Post - Approval Required

**Platform**: {platform}
**From**: {draft_file.name}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Content

{content}

---

## Next Steps

1. Review the content above
2. If approved, move this file to `vault/Social_Media/Approved/` (it will be auto-posted)
3. If rejected, delete this file

⚠️ Posts are executed in order of approval.
"""

            approval_file.write_text(approval_content, encoding='utf-8')
            logger.info(f"✅ [{platform.upper()}] Approval request created: {approval_name}")

            # Move draft to Posted folder to mark as processed
            posted_file = self.social_media / 'Posted' / f"{platform}_{draft_file.stem}_draft.md"
            posted_file.parent.mkdir(parents=True, exist_ok=True)
            draft_file.rename(posted_file)

        except Exception as e:
            logger.error(f"❌ Failed to create approval: {e}")


def main():
    parser = argparse.ArgumentParser(description='Social Media Draft Watcher')
    parser.add_argument('--vault', required=True, help='Path to vault')

    args = parser.parse_args()
    vault_path = args.vault

    # Watch Social_Media draft folders
    social_media = Path(vault_path) / 'Social_Media'
    draft_folders = [
        social_media / 'Twitter_Drafts',
        social_media / 'Facebook_Drafts',
        social_media / 'Instagram_Drafts',
        social_media / 'LinkedIn_Drafts'
    ]

    # Create folders if they don't exist
    for folder in draft_folders:
        folder.mkdir(parents=True, exist_ok=True)

    handler = DraftApprovalHandler(vault_path)
    observer = Observer()

    for folder in draft_folders:
        observer.schedule(handler, str(folder), recursive=False)
        logger.info(f"👁️  Watching: {folder.name}")

    observer.start()
    logger.info("🚀 Social Media Watcher started. Press Ctrl+C to stop.\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n⛔ Stopping watcher...")
        observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
