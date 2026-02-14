"""
Git Sync Module - Vault synchronization between cloud and local
Handles claim-by-move rule and vault persistence via GitHub
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

try:
    import git
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

logger = logging.getLogger('GitSync')


class GitSync:
    """
    Synchronizes vault between cloud and local via Git.

    Agent modes:
    - cloud-agent: creates drafts, syncs via git
    - local-agent: consumes drafts, executes, syncs via git

    Claim-by-move: Files moved to In_Progress/<agent>/ are locked by that agent
    """

    def __init__(self, vault_path: str, agent_name: str = "cloud-agent", dry_run: bool = False):
        """
        Args:
            vault_path: Path to Obsidian vault
            agent_name: Either "cloud-agent" or "local-agent"
            dry_run: If True, don't actually push to remote
        """
        self.vault_path = Path(vault_path)
        self.agent_name = agent_name
        self.dry_run = dry_run
        self.repo = None

        # Vault folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress_dir = self.vault_path / 'In_Progress' / agent_name
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.updates = self.vault_path / 'Updates'

        # Ensure directories exist
        for d in [self.needs_action, self.in_progress_dir, self.pending_approval,
                  self.approved, self.done, self.updates]:
            d.mkdir(parents=True, exist_ok=True)

        if GIT_AVAILABLE:
            self._init_repo()

        logger.info(f"GitSync initialized | agent={agent_name} | vault={vault_path} | dry_run={dry_run}")

    def _init_repo(self):
        """Initialize or open existing git repository"""
        try:
            # Check if vault is in a git repo
            self.repo = git.Repo(str(self.vault_path), search_parent_directories=True)
            logger.info(f"Using existing git repo: {self.repo.working_dir}")
        except git.InvalidGitRepositoryError:
            logger.error("Vault is not in a git repository. Set up git first.")
            self.repo = None

    def pull_latest(self) -> bool:
        """
        Pull latest changes from remote (get approvals/updates from other agent)
        """
        if not self.repo:
            logger.warning("Git repo not available")
            return False

        try:
            logger.info("Pulling latest changes from origin...")
            origin = self.repo.remote('origin')
            origin.pull()
            logger.info("Pull successful")
            return True
        except Exception as e:
            logger.error(f"Pull failed: {e}")
            return False

    def claim_file(self, file_path: Path) -> bool:
        """
        Claim a file by moving it to In_Progress/<agent>/
        Implements claim-by-move rule

        Returns: True if successfully claimed, False if already claimed by another agent
        """
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False

        # Check if already claimed by another agent
        for other_agent_dir in (self.vault_path / 'In_Progress').glob('*'):
            if other_agent_dir.name != self.agent_name:
                if (other_agent_dir / file_path.name).exists():
                    logger.warning(f"File already claimed by {other_agent_dir.name}")
                    return False

        # Move to our In_Progress folder
        dest = self.in_progress_dir / file_path.name
        if dest.exists():
            ts = datetime.now().strftime('%H%M%S')
            dest = self.in_progress_dir / f"{file_path.stem}_{ts}{file_path.suffix}"

        file_path.rename(dest)
        logger.info(f"Claimed file: {dest.name}")
        return True

    def release_file(self, file_path: Path, dest_folder: Path) -> bool:
        """
        Release a claimed file by moving it elsewhere

        Args:
            file_path: Current path (in In_Progress/<agent>/)
            dest_folder: Destination folder (Approved, Done, etc.)
        """
        if not file_path.exists():
            logger.warning(f"File does not exist: {file_path}")
            return False

        dest = dest_folder / file_path.name
        if dest.exists():
            ts = datetime.now().strftime('%H%M%S')
            dest = dest_folder / f"{file_path.stem}_{ts}{file_path.suffix}"

        file_path.rename(dest)
        logger.info(f"Released file to {dest_folder.name}: {dest.name}")
        return True

    def commit_and_push(self, message: str) -> bool:
        """
        Stage, commit, and push all changes to remote

        Args:
            message: Commit message
        """
        if not self.repo:
            logger.warning("Git repo not available")
            return False

        if self.dry_run:
            logger.info(f"[DRY RUN] Would commit and push: {message}")
            return True

        try:
            # Stage all changes
            self.repo.index.add(['.'])

            # Check if there are changes to commit
            if self.repo.index.diff('HEAD'):
                self.repo.index.commit(message)
                logger.info(f"Committed: {message}")
            else:
                logger.info("No changes to commit")

            # Push to origin
            try:
                origin = self.repo.remote('origin')
                origin.push()
                logger.info("Pushed to origin")
            except Exception as push_error:
                logger.warning(f"No remote 'origin' configured: {push_error}")

            return True
        except Exception as e:
            logger.error(f"Commit/push failed: {e}")
            return False

    def sync_cycle(self) -> dict:
        """
        One full sync cycle: pull, work, push
        Returns: dict with sync results
        """
        result = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_name,
            'pulled': False,
            'pushed': False,
            'changes': 0,
            'errors': []
        }

        try:
            # Step 1: Pull latest (get other agent's changes)
            if self.pull_latest():
                result['pulled'] = True
            else:
                result['errors'].append("Pull failed")

            # Step 2: Push our changes
            commit_msg = f"Sync from {self.agent_name} at {datetime.now().isoformat()}"
            if self.commit_and_push(commit_msg):
                result['pushed'] = True
            else:
                result['errors'].append("Push failed")

            logger.info(f"Sync cycle complete: {result}")
            return result

        except Exception as e:
            logger.error(f"Sync cycle error: {e}")
            result['errors'].append(str(e))
            return result


def git_sync_loop(vault_path: str, agent_name: str = "cloud-agent", interval: int = 300, dry_run: bool = False):
    """
    Background thread function - periodically syncs vault

    Args:
        vault_path: Path to vault
        agent_name: cloud-agent or local-agent
        interval: Seconds between syncs (default 5 min)
        dry_run: If True, don't actually push
    """
    syncer = GitSync(vault_path, agent_name, dry_run)

    logger.info(f"Starting git sync loop (interval={interval}s)")

    while True:
        try:
            syncer.sync_cycle()
            time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Git sync loop stopped by user")
            break
        except Exception as e:
            logger.error(f"Git sync error: {e}")
            time.sleep(interval)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    if len(sys.argv) < 2:
        print("Usage: python git_sync.py <vault_path> [agent_name] [--dry-run]")
        sys.exit(1)

    vault = sys.argv[1]
    agent = sys.argv[2] if len(sys.argv) > 2 else "cloud-agent"
    dry_run = "--dry-run" in sys.argv

    git_sync_loop(vault, agent, interval=300, dry_run=dry_run)
