#!/usr/bin/env python3
"""
Twitter API v2 using Tweepy Library
Official Twitter API with OAuth 1.0a - Simplest & Most Reliable!

Usage:
    python post_twitter_tweepy.py --content "Your tweet here"
"""

import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

try:
    import tweepy
except ImportError:
    print("❌ tweepy not installed. Installing...")
    os.system('pip install tweepy')
    import tweepy


def post_tweet(content: str) -> bool:
    """Post a tweet using Tweepy (official library)"""
    try:
        # Get credentials
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([api_key, api_secret, access_token, access_token_secret]):
            print("❌ Twitter credentials not set in .env")
            return False

        print(f"🐦 Posting to Twitter via Tweepy...")
        print(f"Content: {content[:80]}...")

        # Authenticate with OAuth 1.0a User Context
        client = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

        # Post the tweet
        response = client.create_tweet(text=content)

        if response and response.data:
            tweet_id = response.data['id']
            print(f"✅ Tweet posted successfully!")
            print(f"📌 Tweet ID: {tweet_id}")
            print(f"🔗 View: https://twitter.com/huzaifa_xpert/status/{tweet_id}")
            return True
        else:
            print(f"❌ Error: No response data")
            return False

    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(description='Post to Twitter using Tweepy')
    parser.add_argument('--content', required=True, help='Tweet content')
    parser.add_argument('--test', action='store_true', help='Test authentication')

    args = parser.parse_args()

    try:
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        if not all([api_key, api_secret, access_token, access_token_secret]):
            print("❌ Twitter credentials not set in .env")
            return 1

        if args.test:
            print("🔐 Testing Twitter API authentication...")
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            user = client.get_me()
            if user and user.data:
                print(f"✅ Authenticated as: @{user.data.username}")
                print(f"   Name: {user.data.name}")
                print(f"   Ready to post!")
                return 0
            else:
                print("❌ Authentication failed")
                return 1

        success = post_tweet(args.content)
        return 0 if success else 1

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
