#!/usr/bin/env python3
"""
Twitter Manual Login - WSL compatible using xvfb for headed browser.
Run: xvfb-run python scripts/twitter_login_save.py
OR if xvfb not available, use cookie import method.
"""
import asyncio
import sys
import json
from playwright.async_api import async_playwright
from pathlib import Path

STORAGE_PATH = Path(__file__).parent.parent / "vault" / ".twitter_session.json"


async def login_with_xvfb():
    """Open visible browser via xvfb for manual login"""
    print("=" * 50)
    print("TWITTER MANUAL LOGIN (xvfb mode)")
    print("=" * 50)
    print()
    print("Browser khulega - tum manually login karo.")
    print("Login ke baad terminal mein Enter daba dena.")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
        )
        page = await context.new_page()
        await page.goto('https://x.com/login')

        print("Browser open ho gaya. Login karo Twitter pe...")
        print("Jab home page aa jaye, yahan Enter press karo: ", end='', flush=True)
        await asyncio.get_event_loop().run_in_executor(None, input)

        print(f"\nCurrent URL: {page.url}")
        STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
        await context.storage_state(path=str(STORAGE_PATH))
        print(f"Session saved to: {STORAGE_PATH}")
        await browser.close()


async def login_headless_interactive():
    """Headless login - script tells you what's on screen, you tell it what to type"""
    print("=" * 50)
    print("TWITTER INTERACTIVE LOGIN (headless)")
    print("=" * 50)
    print()
    print("Browser headless hai but main tumhe bataunga kya screen pe hai.")
    print("Tum type karo jo enter karna hai.")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
        )
        await context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        page = await context.new_page()

        print("Loading Twitter login...")
        await page.goto('https://x.com/i/flow/login', timeout=30000)
        await asyncio.sleep(5)

        max_steps = 10
        for step in range(max_steps):
            # Describe current page
            inputs = page.locator('input')
            input_count = await inputs.count()

            print(f"\n--- Step {step + 1} ---")
            print(f"URL: {page.url}")

            # Get visible text hints
            labels = page.locator('label, h1, h2, span[role="heading"]')
            for i in range(min(await labels.count(), 5)):
                t = await labels.nth(i).text_content()
                if t and t.strip():
                    print(f"  Label: {t.strip()}")

            if 'home' in page.url or page.url.rstrip('/') == 'https://x.com':
                print("\nLOGIN SUCCESS!")
                STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
                await context.storage_state(path=str(STORAGE_PATH))
                print(f"Session saved to: {STORAGE_PATH}")
                await browser.close()
                return True

            if input_count == 0:
                print("No inputs found. Waiting...")
                await asyncio.sleep(3)
                continue

            # Show inputs
            for i in range(input_count):
                inp_type = await inputs.nth(i).get_attribute('type') or 'text'
                inp_name = await inputs.nth(i).get_attribute('name') or ''
                inp_auto = await inputs.nth(i).get_attribute('autocomplete') or ''
                inp_placeholder = await inputs.nth(i).get_attribute('placeholder') or ''
                visible = await inputs.nth(i).is_visible()
                if visible:
                    print(f"  Input [{i}]: type={inp_type} name={inp_name} placeholder={inp_placeholder}")

            user_input = input("\nKya enter karein? (type value, or 'skip' to just press Enter, or 'quit'): ").strip()

            if user_input.lower() == 'quit':
                break

            # Find the main visible input
            for i in range(input_count):
                visible = await inputs.nth(i).is_visible()
                if visible:
                    if user_input.lower() != 'skip':
                        await inputs.nth(i).fill(user_input)
                    await asyncio.sleep(1)
                    await page.keyboard.press('Enter')
                    break

            await asyncio.sleep(5)

        # Final check
        if 'home' in page.url or page.url.rstrip('/') == 'https://x.com':
            print("\nLOGIN SUCCESS!")
            STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
            await context.storage_state(path=str(STORAGE_PATH))
            print(f"Session saved to: {STORAGE_PATH}")
            await browser.close()
            return True

        print("\nLogin complete nahi hua.")
        await browser.close()
        return False


if __name__ == '__main__':
    if '--headless' in sys.argv:
        asyncio.run(login_headless_interactive())
    else:
        try:
            asyncio.run(login_with_xvfb())
        except Exception as e:
            if 'XServer' in str(e) or 'Target' in str(e) or 'ozone' in str(e).lower():
                print(f"\nHeaded browser fail hua. Trying headless interactive mode...\n")
                asyncio.run(login_headless_interactive())
            else:
                raise
