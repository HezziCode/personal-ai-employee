#!/usr/bin/env python3
"""
Twitter API v2 Official Poster
Uses official Twitter API with bearer token - 100% reliable!

Usage:
    python post_twitter_api.py --content "Your tweet here"
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()


class TwitterAPIClient:
    """Official Twitter API v2 client"""

    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not self.bearer_token:
            raise ValueError("❌ TWITTER_BEARER_TOKEN not set in .env")

        self.headers = {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

    def post_tweet(self, content: str) -> bool:
        """Post a tweet using official API"""
        try:
            print(f"🐦 Posting to Twitter via API...")
            print(f"Content: {content[:80]}...")

            # Twitter API v2 endpoint
            url = 'https://api.twitter.com/2/tweets'

            # Payload
            payload = {'text': content}

            # Make request
            response = requests.post(url, json=payload, headers=self.headers)

            if response.status_code == 201:
                data = response.json()
                tweet_id = data['data']['id']
                print(f"✅ Tweet posted successfully!")
                print(f"📌 Tweet ID: {tweet_id}")
                print(f"🔗 View: https://twitter.com/huzaifa_xpert/status/{tweet_id}")
                return True
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            return False

    def get_user_info(self) -> dict:
        """Get authenticated user info"""
        try:
            url = 'https://api.twitter.com/2/users/me'
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                return response.json()['data']
            else:
                print(f"❌ Could not get user info: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description='Post to Twitter using official API')
    parser.add_argument('--content', required=True, help='Tweet content')
    parser.add_argument('--test', action='store_true', help='Test authentication only')

    args = parser.parse_args()

    try:
        client = TwitterAPIClient()

        # Test authentication
        if args.test:
            print("🔐 Testing Twitter API authentication...")
            user = client.get_user_info()
            if user:
                print(f"✅ Authenticated as: @{user['username']}")
                print(f"   Name: {user['name']}")
                print(f"   Ready to post!")
                return 0
            else:
                print("❌ Authentication failed")
                return 1

        # Post tweet
        success = client.post_tweet(args.content)
        return 0 if success else 1

    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
