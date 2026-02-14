#!/usr/bin/env python3
"""
Social Media Poster MCP Server
Unified automation for Twitter, Facebook, Instagram posting with HITL approval workflow

Usage:
    python social_media_poster.py --vault /path/to/vault [--process-approved]
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('SocialMediaPoster')


class SocialMediaPoster:
    """Unified social media posting orchestrator"""

    def __init__(self, vault_path: str):
        self.vault = Path(vault_path)
        self.social_media = self.vault / 'Social_Media'
        self.twitter_drafts = self.social_media / 'Twitter_Drafts'
        self.facebook_drafts = self.social_media / 'Facebook_Drafts'
        self.instagram_drafts = self.social_media / 'Instagram_Drafts'
        self.linkedin_drafts = self.social_media / 'LinkedIn_Drafts'
        self.approved = self.social_media / 'Approved'
        self.posted = self.social_media / 'Posted'
        self.logs = self.vault / 'Logs'

        # Ensure directories exist
        for d in [self.approved, self.posted, self.logs]:
            d.mkdir(parents=True, exist_ok=True)

    def parse_draft(self, file_path: Path) -> dict:
        """Parse draft markdown file and extract metadata and content"""
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        metadata = {}
        body_start = 0

        # Parse YAML frontmatter
        if lines[0].strip() == '---':
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    body_start = i + 1
                    break
                if ':' in line:
                    key, val = line.split(':', 1)
                    metadata[key.strip()] = val.strip()

        # Extract post content (after frontmatter)
        body = '\n'.join(lines[body_start:]).strip()
        return {
            'path': file_path,
            'name': file_path.stem,
            'metadata': metadata,
            'body': body
        }

    def create_approval_request(self, platform: str, draft: dict) -> Path:
        """Move draft to Approved folder for human approval"""
        approval_file = self.approved / f"{platform.upper()}_{draft['name']}_approval.md"

        approval_content = f"""---
platform: {platform}
status: pending_approval
created: {datetime.now().isoformat()}
original_draft: {draft['path'].name}
---

# {platform.title()} Post Awaiting Approval

**Platform**: {platform}
**Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content

{draft['body']}

---

## Action Required

Move to `{self.posted}` to post, or delete to reject.

"""
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"✅ Approval request created: {approval_file.name}")
        return approval_file

    def post_twitter(self, content: str, dry_run: bool = False) -> bool:
        """Post to Twitter using Playwright automation"""
        try:
            username = os.getenv('TWITTER_EMAIL')
            password = os.getenv('TWITTER_PASSWORD')

            if not username or not password:
                logger.error("❌ TWITTER_EMAIL and TWITTER_PASSWORD not set")
                return False

            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context_options = {
                    'viewport': {'width': 1280, 'height': 720},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }

                session_path = Path('playwright/.auth/twitter_session')
                if session_path.exists():
                    context_options['storage_state'] = str(session_path)

                context = browser.new_context(**context_options)
                page = context.new_page()

                page.goto('https://twitter.com/home')

                if 'login' in page.url:
                    logger.info("🔑 Logging into Twitter...")
                    page.fill('input[autocomplete="username"]', username)
                    page.click('text=Next')
                    page.wait_for_selector('input[type="password"]', timeout=10000)
                    page.fill('input[type="password"]', password)
                    page.click('text=Log in')
                    page.wait_for_url('https://twitter.com/home', timeout=30000)
                    context.storage_state(path=str(session_path))

                if dry_run:
                    logger.info(f"[DRY RUN] Would tweet:\n{content}")
                    browser.close()
                    return True

                logger.info("📝 Composing tweet...")
                page.click('[data-testid="SideNav_NewTweet_Button"]', timeout=10000)
                page.wait_for_selector('[data-testid="tweetTextarea_0"]', timeout=10000)

                editor = page.locator('[data-testid="tweetTextarea_0"]')
                editor.fill(content)
                page.wait_for_timeout(2000)

                logger.info("📤 Posting tweet...")
                page.click('[data-testid="tweetButton"]', timeout=5000)
                page.wait_for_timeout(3000)

                browser.close()
                logger.info("✅ Tweet posted successfully!")
                return True

        except Exception as e:
            logger.error(f"❌ Twitter post failed: {e}")
            return False

    def post_facebook(self, content: str, dry_run: bool = False) -> bool:
        """Post to Facebook Page using Graph API"""
        try:
            import requests

            page_id = os.getenv('FACEBOOK_PAGE_ID')
            page_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

            if not page_id or not page_token:
                # Try deriving from user token
                user_token = os.getenv('FACEBOOK_USER_ACCESS_TOKEN')
                if user_token:
                    r = requests.get(f'https://graph.facebook.com/v19.0/me/accounts?access_token={user_token}')
                    data = r.json()
                    if 'data' in data and len(data['data']) > 0:
                        page_id = data['data'][0]['id']
                        page_token = data['data'][0]['access_token']

            if not page_id or not page_token:
                logger.error("❌ FACEBOOK_PAGE_ID or token not configured")
                return False

            if dry_run:
                logger.info(f"[DRY RUN] Would post on Facebook:\n{content}")
                return True

            url = f'https://graph.facebook.com/v19.0/{page_id}/feed'
            payload = {'message': content, 'access_token': page_token}

            logger.info("📤 Posting to Facebook via Graph API...")
            response = requests.post(url, data=payload)

            if response.status_code == 200:
                post_id = response.json().get('id', 'unknown')
                logger.info(f"✅ Facebook post successful! ID: {post_id}")
                logger.info(f"🔗 https://www.facebook.com/{post_id}")
                return True
            else:
                error = response.json().get('error', {}).get('message', response.text)
                logger.error(f"❌ Facebook post failed: {error}")
                return False

        except Exception as e:
            logger.error(f"❌ Facebook post failed: {e}")
            return False

    def post_instagram(self, content: str, image_url: str = None, dry_run: bool = False) -> bool:
        """Post to Instagram using Graph API"""
        try:
            import requests

            ig_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
            page_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')

            if not ig_account_id or not page_token:
                logger.error("❌ INSTAGRAM_BUSINESS_ACCOUNT_ID or token not configured")
                logger.info("   Link Instagram Business account to your Facebook Page first")
                return False

            if not image_url:
                logger.error("❌ Instagram requires an image_url for posting")
                return False

            if dry_run:
                logger.info(f"[DRY RUN] Would post on Instagram:\n{content}")
                return True

            # Step 1: Create media container
            logger.info("📸 Creating Instagram media container...")
            container_url = f'https://graph.facebook.com/v19.0/{ig_account_id}/media'
            r1 = requests.post(container_url, data={
                'image_url': image_url, 'caption': content, 'access_token': page_token
            })

            if r1.status_code != 200:
                error = r1.json().get('error', {}).get('message', r1.text)
                logger.error(f"❌ Container creation failed: {error}")
                return False

            container_id = r1.json().get('id')

            # Step 2: Publish
            logger.info("📤 Publishing Instagram post...")
            r2 = requests.post(
                f'https://graph.facebook.com/v19.0/{ig_account_id}/media_publish',
                data={'creation_id': container_id, 'access_token': page_token}
            )

            if r2.status_code == 200:
                media_id = r2.json().get('id', 'unknown')
                logger.info(f"✅ Instagram post successful! Media ID: {media_id}")
                return True
            else:
                error = r2.json().get('error', {}).get('message', r2.text)
                logger.error(f"❌ Instagram publish failed: {error}")
                return False

        except Exception as e:
            logger.error(f"❌ Instagram post failed: {e}")
            return False

    def post_linkedin(self, content: str, dry_run: bool = False) -> bool:
        """Post to LinkedIn using existing linkedin-poster MCP"""
        try:
            logger.info("📝 Posting to LinkedIn...")
            result = subprocess.run(
                [sys.executable, 'mcp_servers/linkedin-poster/linkedin_poster.py',
                 '--content', content, '--vault', str(self.vault)],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                logger.info("✅ LinkedIn post created successfully!")
                return True
            else:
                logger.error(f"❌ LinkedIn post failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"❌ LinkedIn post failed: {e}")
            return False

    def process_approved_posts(self, dry_run: bool = False) -> None:
        """Check Approved folder and execute posts"""
        if not self.approved.exists():
            logger.info("✅ No approved posts found")
            return

        for approval_file in self.approved.glob('*.md'):
            draft = self.parse_draft(approval_file)
            platform = draft['metadata'].get('platform', 'unknown')

            logger.info(f"\n🔄 Processing {platform.upper()} post: {draft['name']}")

            # Execute post
            success = False
            if platform.lower() == 'twitter':
                success = self.post_twitter(draft['body'], dry_run=dry_run)
            elif platform.lower() == 'facebook':
                success = self.post_facebook(draft['body'], dry_run=dry_run)
            elif platform.lower() == 'instagram':
                success = self.post_instagram(draft['body'], dry_run=dry_run)
            elif platform.lower() == 'linkedin':
                success = self.post_linkedin(draft['body'], dry_run=dry_run)

            # Move to Posted if successful
            if success:
                posted_file = self.posted / f"{platform}_{draft['name']}_posted.md"
                posted_file.write_text(approval_file.read_text(encoding='utf-8'), encoding='utf-8')

                # Log
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'platform': platform,
                    'status': 'posted',
                    'draft': draft['name']
                }
                log_file = self.logs / f"social_media_{datetime.now().strftime('%Y%m%d')}.jsonl"
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')

                approval_file.unlink()
                logger.info(f"✅ Post moved to {posted_file.name}")
            else:
                # Log failure
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'platform': platform,
                    'status': 'failed',
                    'draft': draft['name']
                }
                log_file = self.logs / f"social_media_{datetime.now().strftime('%Y%m%d')}.jsonl"
                with open(log_file, 'a') as f:
                    f.write(json.dumps(log_entry) + '\n')

                logger.warning(f"⚠️ Post failed - keeping in Approved folder for retry")

    def create_draft_approval(self, platform: str, content: str) -> Path:
        """Helper to create draft and approval request"""
        draft = {
            'path': None,
            'body': content,
            'metadata': {'platform': platform}
        }
        return self.create_approval_request(platform, draft)


def main():
    parser = argparse.ArgumentParser(description='Social Media Poster - Unified posting automation')
    parser.add_argument('--vault', required=True, help='Path to vault')
    parser.add_argument('--process-approved', action='store_true', help='Process approved posts from Approved folder')
    parser.add_argument('--dry-run', action='store_true', help='Test without actually posting')

    args = parser.parse_args()

    poster = SocialMediaPoster(args.vault)

    if args.process_approved:
        logger.info("🚀 Processing approved social media posts...\n")
        poster.process_approved_posts(dry_run=args.dry_run)
    else:
        logger.info("❓ No action specified. Use --process-approved to post approved content")


if __name__ == '__main__':
    main()
