"""
File System Watcher
Monitors the Inbox folder for new files and creates action items

This is the simplest watcher - great for testing the system!
Drop any file in the Inbox folder and it will be processed.
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher


class InboxHandler(FileSystemEventHandler):
    """Handles file system events in the Inbox folder"""

    def __init__(self, watcher: 'FileWatcher'):
        self.watcher = watcher
        self.processed_files = set()

    def on_created(self, event):
        """Called when a file is created in the Inbox"""
        if event.is_directory:
            return

        filepath = Path(event.src_path)

        # Skip hidden files and already processed
        if filepath.name.startswith('.'):
            return
        if str(filepath) in self.processed_files:
            return

        self.processed_files.add(str(filepath))
        self.watcher.logger.info(f'New file detected: {filepath.name}')

        # Create action file
        self.watcher.create_action_file(filepath)


class FileWatcher(BaseWatcher):
    """
    Watches the Inbox folder for new files
    Creates action items in Needs_Action folder
    """

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=5)
        self.observer = None
        self.handler = InboxHandler(self)

    def check_for_updates(self) -> list:
        """Check for existing files in Inbox (for initial scan)"""
        files = []
        for filepath in self.inbox.iterdir():
            if filepath.is_file() and not filepath.name.startswith('.'):
                files.append(filepath)
        return files

    def create_action_file(self, filepath: Path) -> Path:
        """Create an action file for a dropped file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Determine file type and priority
        file_ext = filepath.suffix.lower()
        priority = 'normal'
        file_type = 'unknown'

        if file_ext in ['.pdf', '.doc', '.docx']:
            file_type = 'document'
            priority = 'normal'
        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
            file_type = 'image'
            priority = 'low'
        elif file_ext in ['.xlsx', '.xls', '.csv']:
            file_type = 'spreadsheet'
            priority = 'high'  # Could be financial
        elif file_ext in ['.txt', '.md']:
            file_type = 'text'
            priority = 'normal'

        # Create the action file content
        content = f'''---
type: file_drop
source: inbox
original_name: {filepath.name}
file_type: {file_type}
size_bytes: {filepath.stat().st_size}
created: {datetime.now().isoformat()}
priority: {priority}
status: pending
---

# New File: {filepath.name}

A new file was dropped in the Inbox folder.

## File Details
- **Name**: {filepath.name}
- **Type**: {file_type}
- **Size**: {filepath.stat().st_size} bytes
- **Detected**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Suggested Actions

- [ ] Review file contents
- [ ] Categorize appropriately
- [ ] Process or archive

## Notes

Add any notes here after processing.

---
*Created by File Watcher*
'''

        # Write action file
        action_filename = f'FILE_{timestamp}_{filepath.stem}.md'
        action_path = self.needs_action / action_filename
        action_path.write_text(content)

        # Log the action
        self.log_action('file_detected', {
            'original_file': filepath.name,
            'action_file': action_filename,
            'file_type': file_type,
            'priority': priority
        })

        self.logger.info(f'Created action: {action_filename}')
        return action_path

    def run(self):
        """Run the file watcher using watchdog"""
        self.logger.info(f'Starting File Watcher')
        self.logger.info(f'Watching: {self.inbox}')

        # Process any existing files first
        existing = self.check_for_updates()
        for filepath in existing:
            self.create_action_file(filepath)
            self.logger.info(f'Processed existing file: {filepath.name}')

        # Set up watchdog observer
        self.observer = Observer()
        self.observer.schedule(self.handler, str(self.inbox), recursive=False)
        self.observer.start()

        self.logger.info('File watcher is now running. Press Ctrl+C to stop.')

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info('Stopping file watcher...')
            self.observer.stop()

        self.observer.join()
        self.logger.info('File watcher stopped.')


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description='File System Watcher for AI Employee')
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

    watcher = FileWatcher(str(vault_path))
    watcher.run()


if __name__ == '__main__':
    main()
