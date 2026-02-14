"""
LinkedIn Auto-Poster
Uses Playwright to automate LinkedIn posting

Usage:
    python linkedin_poster.py --content "Post content here" [--dry-run]
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('LinkedInPoster')


class LinkedInPoster:
    """
    Automates LinkedIn posting using Playwright
    """

    def __init__(self, email: str, password: str, session_path: str = None):
        self.email = email
        self.password = password
        self.session_path = Path(session_path or 'playwright/.auth/linkedin_session')
        self.session_path.parent.mkdir(parents=True, exist_ok=True)

    def login(self, page):
        """Login to LinkedIn"""
        logger.info("Navigating to LinkedIn...")
        page.goto('https://www.linkedin.com/login')

        logger.info("Entering credentials...")
        page.fill('input[name="session_key"]', self.email)
        page.fill('input[name="session_password"]', self.password)

        logger.info("Clicking sign in...")
        page.click('button[type="submit"]')

        # Wait for login to complete
        try:
            page.wait_for_url('https://www.linkedin.com/feed/*', timeout=30000)
            logger.info("✅ Login successful")
            return True
        except PlaywrightTimeout:
            # Check if 2FA or verification required
            if 'challenge' in page.url or 'checkpoint' in page.url:
                logger.error("❌ 2FA or verification required. Please login manually first.")
                return False
            logger.error("❌ Login failed or timed out")
            return False

    def post_content(self, page, content: str, dry_run: bool = False):
        """Post content to LinkedIn"""
        if dry_run:
            logger.info(f"[DRY RUN] Would post:\n{content}")
            return True

        try:
            logger.info("Opening post dialog...")

            # Click "Start a post" button
            page.click('button[aria-label*="Start a post"]', timeout=10000)

            # Wait for editor to appear
            page.wait_for_selector('[data-test-ql-editor-contenteditable]', timeout=10000)

            logger.info("Entering content...")
            # Type content
            editor = page.locator('[data-test-ql-editor-contenteditable]')
            editor.fill(content)

            # Wait a bit to look human
            page.wait_for_timeout(2000)

            logger.info("Clicking Post button...")
            # Click Post button
            page.click('button[aria-label*="Post"]', timeout=5000)

            # Wait for post to complete
            page.wait_for_timeout(3000)

            logger.info("✅ Posted successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to post: {e}")
            return False

    def run(self, content: str, dry_run: bool = False, headless: bool = True):
        """Main execution"""
        with sync_playwright() as p:
            # Launch browser
            logger.info(f"Launching browser (headless={headless})...")
            browser = p.chromium.launch(
                headless=headless,
                args=['--no-sandbox', '--disable-setuid-sandbox']
            )

            # Create context with saved session if exists
            context_options = {
                'viewport': {'width': 1280, 'height': 720},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            if self.session_path.exists():
                logger.info("Using saved session...")
                context_options['storage_state'] = str(self.session_path)

            context = browser.new_context(**context_options)
            page = context.new_page()

            # Check if already logged in
            page.goto('https://www.linkedin.com/feed')

            if 'login' in page.url:
                logger.info("Not logged in, attempting login...")
                if not self.login(page):
                    browser.close()
                    return False

                # Save session
                logger.info("Saving session...")
                context.storage_state(path=str(self.session_path))
            else:
                logger.info("Already logged in!")

            # Post content
            success = self.post_content(page, content, dry_run)

            # Close browser
            browser.close()

            return success


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Poster')
    parser.add_argument('--content', required=True, help='Post content')
    parser.add_argument('--dry-run', action='store_true', help='Test without actually posting')
    parser.add_argument('--headless', action='store_true', help='Run in headless mode')
    parser.add_argument('--email', help='LinkedIn email (or set LINKEDIN_EMAIL env var)')
    parser.add_argument('--password', help='LinkedIn password (or set LINKEDIN_PASSWORD env var)')

    args = parser.parse_args()

    # Get credentials
    email = args.email or os.getenv('LINKEDIN_EMAIL')
    password = args.password or os.getenv('LINKEDIN_PASSWORD')

    if not email or not password:
        logger.error("LinkedIn credentials required!")
        logger.error("Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD env vars or use --email --password flags")
        sys.exit(1)

    # Create poster
    poster = LinkedInPoster(email, password)

    # Run
    success = poster.run(args.content, dry_run=args.dry_run, headless=args.headless)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
