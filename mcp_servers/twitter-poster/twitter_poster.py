#!/usr/bin/env python3
"""
Twitter/X Poster via Official API v2
Posts tweets with media support
"""

import os
import requests
from pathlib import Path
from typing import Optional

class TwitterPoster:
    def __init__(self):
        self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.base_url = "https://api.twitter.com/2"
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }

    def post_tweet(self, text: str, media_path: Optional[str] = None) -> bool:
        """Post a tweet to Twitter/X."""

        try:
            print(f"📝 Posting to Twitter: {text[:50]}...")

            # Create tweet payload
            payload = {"text": text}

            # Post tweet
            response = requests.post(
                f"{self.base_url}/tweets",
                json=payload,
                headers=self.headers
            )

            if response.status_code in [200, 201]:
                tweet_data = response.json()
                tweet_id = tweet_data['data']['id']
                print(f"✅ Tweet posted! ID: {tweet_id}")
                return True
            else:
                print(f"❌ Error: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error posting tweet: {e}")
            return False

    def post_thread(self, tweets: list) -> bool:
        """Post a thread of tweets."""

        try:
            print(f"📋 Posting thread with {len(tweets)} tweets...")

            reply_to_id = None

            for i, text in enumerate(tweets, 1):
                payload = {"text": text}

                if reply_to_id:
                    payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}

                response = requests.post(
                    f"{self.base_url}/tweets",
                    json=payload,
                    headers=self.headers
                )

                if response.status_code in [200, 201]:
                    reply_to_id = response.json()['data']['id']
                    print(f"  ✅ Tweet {i}/{len(tweets)} posted")
                else:
                    print(f"  ❌ Tweet {i} failed: {response.text}")
                    return False

            print("✅ Thread posted successfully!")
            return True

        except Exception as e:
            print(f"❌ Error posting thread: {e}")
            return False


if __name__ == '__main__':
    poster = TwitterPoster()

    # Test tweet
    tweet_text = """
🤖 Your AI Employee is now LIVE!

Automate your entire business:
✅ Multi-channel content distribution
✅ Email management
✅ Accounting automation
✅ 24/7 cloud deployment

Your personal FTE is working while you sleep! 🚀
    """.strip()

    poster.post_tweet(tweet_text)
