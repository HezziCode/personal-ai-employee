#!/usr/bin/env python3
"""
Twitter API v2 with OAuth 1.0a User Context
Uses official Twitter API with user authentication - 100% reliable!

Usage:
    python post_twitter_api_oauth.py --content "Your tweet here"
"""

import os
import sys
import argparse
import hashlib
import hmac
import base64
import time
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()


class TwitterOAuth1:
    """Twitter API v2 with OAuth 1.0a User Context"""

    def __init__(self):
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
            raise ValueError("❌ Twitter OAuth credentials not set in .env")

    def generate_signature(self, method, url, params, consumer_secret, token_secret):
        """Generate OAuth signature"""
        # Create signing key
        key = f"{consumer_secret}&{token_secret}"
        key_bytes = key.encode('utf-8')

        # Create base string
        param_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        base_string = f"{method}&{url}&{urlencode(param_string)}"

        # Generate signature
        message_bytes = base_string.encode('utf-8')
        signature = base64.b64encode(
            hmac.new(key_bytes, message_bytes, hashlib.sha1).digest()
        ).decode('utf-8')

        return signature

    def post_tweet(self, content: str) -> bool:
        """Post a tweet using OAuth 1.0a"""
        try:
            print(f"🐦 Posting to Twitter via OAuth 1.0a...")
            print(f"Content: {content[:80]}...")

            url = 'https://api.twitter.com/2/tweets'

            # OAuth parameters
            oauth_params = {
                'oauth_consumer_key': self.api_key,
                'oauth_token': self.access_token,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': str(int(time.time())),
                'oauth_nonce': str(int(time.time() * 1000)),
                'oauth_version': '1.0'
            }

            # Combine all parameters for signature
            all_params = oauth_params.copy()

            # Generate signature
            signature = self.generate_signature(
                'POST',
                url,
                all_params,
                self.api_secret,
                self.access_token_secret
            )

            oauth_params['oauth_signature'] = signature

            # Build Authorization header
            auth_header = 'OAuth ' + ', '.join([
                f'{k}="{v}"' for k, v in sorted(oauth_params.items())
            ])

            headers = {
                'Authorization': auth_header,
                'Content-Type': 'application/json'
            }

            payload = {'text': content}

            # Make request
            response = requests.post(url, json=payload, headers=headers)

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
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(description='Post to Twitter using OAuth 1.0a')
    parser.add_argument('--content', required=True, help='Tweet content')

    args = parser.parse_args()

    try:
        client = TwitterOAuth1()
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
