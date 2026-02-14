#!/usr/bin/env python3
"""
Twitter Browser Use Poster - Using browser-use library with Claude vision
"""
import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

try:
    from browser_use import Agent
except ImportError:
    print("❌ browser-use not properly installed")
    sys.exit(1)

async def post_to_twitter_browser_use(content: str):
    """Post to Twitter using browser-use with Claude vision"""

    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')

    if not email or not password:
        print("❌ TWITTER_EMAIL and TWITTER_PASSWORD not set")
        return False

    print(f"🐦 Twitter Browser Use (Vision-based)")
    print(f"Account: {email}")
    print(f"Content: {content[:80]}...")

    try:
        # Create agent with Claude vision
        agent = Agent(
            task=f"""
            1. Go to Twitter (twitter.com)
            2. Log in with email: {email} and password: {password}
            3. Open compose/new tweet
            4. Type this tweet:
            {content}
            5. Click Post/Tweet button
            6. Confirm tweet was posted

            Take screenshots to verify each step. Use visual understanding to find buttons and inputs.
            """,
            llm_config={
                "model": "claude-opus-4-5",  # Use Claude's vision capabilities
                "temperature": 0.7,
            }
        )

        print("🚀 Starting browser-use agent with Claude vision...")
        result = await agent.run(max_steps=10)

        if result and "success" in str(result).lower():
            print("✅ Tweet posted successfully! 🎉")
            return True
        else:
            print(f"⚠️ Result: {result}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    content = """🤖 Meet Your New AI Employee

Introducing our revolutionary AI automation system that works 24/7 so you don't have to!

✅ Email management
✅ Social media posting
✅ Report generation
✅ Task automation

Stop wasting time on manual work. Let's automate your life. 🚀

#AI #Automation #FutureOfWork #Innovation"""

    # Run async function
    success = asyncio.run(post_to_twitter_browser_use(content))
    sys.exit(0 if success else 1)
