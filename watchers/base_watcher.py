"""
Base Watcher - Template for all watchers
All watchers inherit from this class
"""

import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class BaseWatcher(ABC):
    """Base class for all watchers (Gmail, WhatsApp, File System, etc.)"""

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the watcher

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default 60)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.inbox = self.vault_path / 'Inbox'
        self.logs = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)

        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.inbox.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check for new items to process
        Must be implemented by child classes

        Returns:
            List of new items to process
        """
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a .md file in Needs_Action folder
        Must be implemented by child classes

        Args:
            item: The item to create an action file for

        Returns:
            Path to the created file
        """
        pass

    def log_action(self, action_type: str, details: dict):
        """Log an action to the daily log file"""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'watcher': self.__class__.__name__,
            'action_type': action_type,
            'details': details
        }

        # Load existing logs or create new
        if log_file.exists():
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        self.logger.info(f"Logged: {action_type}")

    def run(self):
        """Main loop - continuously check for updates"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')

        while True:
            try:
                items = self.check_for_updates()
                for item in items:
                    filepath = self.create_action_file(item)
                    self.logger.info(f'Created action file: {filepath}')
                    self.log_action('file_created', {'path': str(filepath)})
            except KeyboardInterrupt:
                self.logger.info('Watcher stopped by user')
                break
            except Exception as e:
                self.logger.error(f'Error in watcher loop: {e}')
                self.log_action('error', {'error': str(e)})

            time.sleep(self.check_interval)


if __name__ == '__main__':
    print("This is a base class. Use specific watchers like file_watcher.py")
