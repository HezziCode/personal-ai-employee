#!/usr/bin/env python3
"""
Twitter/X Poster
Uses Playwright to automate Twitter posting

Usage:
    python twitter_poster.py --content "Tweet content" [--dry-run]
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('TwitterPoster')


class TwitterPoster:
    """Automates Twitter posting using Playwright"""

    def __init__(self, username: str, password: str, session_path: str = None):
        self.username = username
        self.password = password
        self.session_path = Path(session_path or 'playwright/.auth/twitter_session')
        self.session_path.parent.mkdir(parents=True, exist_ok=True)

    def login(self, page):
        """Login to Twitter"""
        logger.info("Navigating to Twitter login...")
        page.goto('https://twitter.com/login')

        logger.info("Entering username...")
        page.fill('input[autocomplete="username"]', self.username)
        page.click('text=Next')

        # Wait for password field
        page.wait_for_selector('input[type="password"]', timeout=10000)

        logger.info("Entering password...")
        page.fill('input[type="password"]', self.password)
        page.click('text=Log in')

        # Wait for home page
        try:
            page.wait_for_url('https://twitter.com/home', timeout=30000)
            logger.info("✅ Login successful")
            return True
        except PlaywrightTimeout:
            logger.error("❌ Login failed or verification required")
            return False

    def post_tweet(self, page, content: str, dry_run: bool = False):
        """Post a tweet"""
        if dry_run:
            logger.info(f"[DRY RUN] Would tweet:\n{content}")
            return True

        try:
            logger.info("Opening compose dialog...")

            # Click compose button
            page.click('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)

            # Wait for editor
            page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)

            logger.info("Entering tweet content...")
            editor = page.locator('[data-testid="tweetTextarea_0"]')
            editor.fill(content)

            # Wait to look human
            page.wait_for_timeout(2000)

            logger.info("Clicking Tweet button...")
            page.click('[data-testid="tweetButton"]', timeout=5000)

            # Wait for post to complete
            page.wait_for_timeout(3000)

            logger.info("✅ Tweet posted!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to tweet: {e}")
            return False

    def run(self, content: str, dry_run: bool = False, headless: bool = True):
        """Main execution"""
        with sync_playwright() as p:
            logger.info(f"Launching browser (headless={headless})...")
            browser = p.chromium.launch(headless=headless)

            context_options = {
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            if self.session_path.exists():
                context_options['storage_state'] = str(self.session_path)

            context = browser.new_context(**context_options)
            page = context.new_page()

            page.goto('https://twitter.com/home')

            if 'login' in page.url:
                if not self.login(page):
                    browser.close()
                    return False
                context.storage_state(path=str(self.session_path))

            success = self.post_tweet(page, content, dry_run)
            browser.close()
            return success


def main():
    parser = argparse.ArgumentParser(description='Twitter Poster')
    parser.add_argument('--content', required=True, help='Tweet content')
    parser.add_argument('--dry-run', action='store_true', help='Test without posting')
    parser.add_argument('--headless', action='store_true', help='Run headless')

    args = parser.parse_args()

    username = os.getenv('TWITTER_USERNAME')
    password = os.getenv('TWITTER_PASSWORD')

    if not username or not password:
        logger.error("Set TWITTER_USERNAME and TWITTER_PASSWORD env vars")
        sys.exit(1)

    poster = TwitterPoster(username, password)
    success = poster.run(args.content, dry_run=args.dry_run, headless=args.headless)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
