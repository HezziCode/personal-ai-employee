#!/usr/bin/env python3
"""
Facebook & Instagram Poster - Graph API Edition
Uses official Meta Graph API for reliable posting (no Playwright needed)

Usage:
    python fb_ig_poster.py --platform facebook --content "Post content" [--dry-run]
    python fb_ig_poster.py --platform instagram --content "Caption" --image-url https://example.com/img.jpg [--dry-run]
"""

import sys
import os
import json
import argparse
from pathlib import Path
from datetime import datetime
import logging
import requests

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('FBIGPoster')

VAULT_PATH = Path(os.getenv('VAULT_PATH', 'vault'))
LOGS_PATH = VAULT_PATH / 'Logs'
LOGS_PATH.mkdir(parents=True, exist_ok=True)


def log_action(platform: str, action: str, result: dict):
    """Log social media action for audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": f"social_media_{action}",
        "platform": platform,
        "actor": "claude_code",
        "result": "success" if result.get("success") else "failure",
        "details": result
    }
    log_file = LOGS_PATH / f"social_media_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
    logger.info(f"Logged to {log_file}")


def get_page_token():
    """Get Page Access Token - first try direct page token, then derive from user token"""
    page_token = os.getenv('FACEBOOK_PAGE_ACCESS_TOKEN')
    if page_token:
        return page_token

    # Derive from user token
    user_token = os.getenv('FACEBOOK_USER_ACCESS_TOKEN')
    if not user_token:
        return None

    url = f'https://graph.facebook.com/v19.0/me/accounts?access_token={user_token}'
    r = requests.get(url)
    data = r.json()
    if 'data' in data and len(data['data']) > 0:
        return data['data'][0]['access_token']
    return None


def post_to_facebook(content: str, dry_run: bool = False) -> dict:
    """Post to Facebook Page using Graph API"""
    page_id = os.getenv('FACEBOOK_PAGE_ID')
    page_token = get_page_token()

    if not page_id or not page_token:
        return {"success": False, "error": "FACEBOOK_PAGE_ID or token not configured"}

    if dry_run:
        logger.info(f"[DRY RUN] Would post on Facebook:\n{content[:100]}...")
        return {"success": True, "dry_run": True, "platform": "facebook"}

    url = f'https://graph.facebook.com/v19.0/{page_id}/feed'
    payload = {
        'message': content,
        'access_token': page_token
    }

    logger.info("Posting to Facebook via Graph API...")
    response = requests.post(url, data=payload)

    if response.status_code == 200:
        data = response.json()
        post_id = data.get('id', 'unknown')
        result = {
            "success": True,
            "platform": "facebook",
            "post_id": post_id,
            "url": f"https://www.facebook.com/{post_id}"
        }
        logger.info(f"Facebook post successful! ID: {post_id}")
        log_action("facebook", "post", result)
        return result
    else:
        error = response.json().get('error', {}).get('message', response.text)
        result = {"success": False, "platform": "facebook", "error": error}
        logger.error(f"Facebook post failed: {error}")
        log_action("facebook", "post", result)
        return result


def post_to_instagram(content: str, image_url: str = None, dry_run: bool = False) -> dict:
    """Post to Instagram using Graph API (requires Business account linked to FB Page)"""
    ig_account_id = os.getenv('INSTAGRAM_BUSINESS_ACCOUNT_ID')
    page_token = get_page_token()

    if not ig_account_id or not page_token:
        return {
            "success": False,
            "error": "INSTAGRAM_BUSINESS_ACCOUNT_ID not set or token missing. "
                     "Link Instagram Business account to your Facebook Page first."
        }

    if not image_url:
        return {
            "success": False,
            "error": "Instagram requires an image_url for posting. "
                     "Provide a publicly accessible image URL."
        }

    if dry_run:
        logger.info(f"[DRY RUN] Would post on Instagram:\n{content[:100]}...")
        return {"success": True, "dry_run": True, "platform": "instagram"}

    # Step 1: Create media container
    logger.info("Creating Instagram media container...")
    container_url = f'https://graph.facebook.com/v19.0/{ig_account_id}/media'
    container_payload = {
        'image_url': image_url,
        'caption': content,
        'access_token': page_token
    }
    r1 = requests.post(container_url, data=container_payload)

    if r1.status_code != 200:
        error = r1.json().get('error', {}).get('message', r1.text)
        result = {"success": False, "platform": "instagram", "error": f"Container creation failed: {error}"}
        log_action("instagram", "post", result)
        return result

    container_id = r1.json().get('id')
    logger.info(f"Container created: {container_id}")

    # Step 2: Publish the container
    logger.info("Publishing Instagram post...")
    publish_url = f'https://graph.facebook.com/v19.0/{ig_account_id}/media_publish'
    publish_payload = {
        'creation_id': container_id,
        'access_token': page_token
    }
    r2 = requests.post(publish_url, data=publish_payload)

    if r2.status_code == 200:
        media_id = r2.json().get('id', 'unknown')
        result = {
            "success": True,
            "platform": "instagram",
            "media_id": media_id,
            "url": f"https://www.instagram.com/"
        }
        logger.info(f"Instagram post successful! Media ID: {media_id}")
        log_action("instagram", "post", result)
        return result
    else:
        error = r2.json().get('error', {}).get('message', r2.text)
        result = {"success": False, "platform": "instagram", "error": f"Publish failed: {error}"}
        log_action("instagram", "post", result)
        return result


def main():
    parser = argparse.ArgumentParser(description='Facebook/Instagram Poster (Graph API)')
    parser.add_argument('--platform', required=True, choices=['facebook', 'instagram'])
    parser.add_argument('--content', required=True, help='Post content/caption')
    parser.add_argument('--image-url', help='Public image URL (required for Instagram)')
    parser.add_argument('--dry-run', action='store_true')

    args = parser.parse_args()

    if args.platform == 'facebook':
        result = post_to_facebook(args.content, dry_run=args.dry_run)
    else:
        result = post_to_instagram(args.content, args.image_url, dry_run=args.dry_run)

    print(json.dumps(result, indent=2))
    sys.exit(0 if result.get('success') else 1)


if __name__ == '__main__':
    main()
