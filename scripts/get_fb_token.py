#!/usr/bin/env python3
"""
Get Facebook Page Access Token with proper permissions via OAuth flow.
Opens browser for user to authorize, then extracts token from redirect URL.
"""
import os
import sys
import time
import urllib.parse
import requests
from dotenv import load_dotenv

load_dotenv()

app_id = os.getenv('FACEBOOK_APP_ID')
app_secret = os.getenv('FACEBOOK_APP_SECRET')

def get_token_via_playwright():
    """Use Playwright to automate the OAuth flow"""
    from playwright.sync_api import sync_playwright

    redirect_uri = 'https://localhost/'
    permissions = 'pages_manage_posts,pages_read_engagement,pages_show_list'

    auth_url = (
        f'https://www.facebook.com/v19.0/dialog/oauth?'
        f'client_id={app_id}&'
        f'redirect_uri={urllib.parse.quote(redirect_uri)}&'
        f'scope={permissions}&'
        f'response_type=token'
    )

    print(f"Opening Facebook OAuth...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()

        # Load Facebook login
        email = os.getenv('FACEBOOK_EMAIL')
        password = os.getenv('FACEBOOK_PASSWORD')

        print("Logging into Facebook...")
        page.goto('https://www.facebook.com/login')
        time.sleep(3)

        # Fill login
        page.fill('#email', email)
        page.fill('#pass', password)
        page.click('[name="login"]')
        time.sleep(5)

        # Check if logged in
        current = page.url
        print(f"After login: {current}")

        if 'checkpoint' in current or 'two_step_verification' in current:
            print("Account needs verification - cannot automate")
            browser.close()
            return None

        # Now navigate to OAuth dialog
        print("Opening OAuth dialog...")
        page.goto(auth_url)
        time.sleep(5)

        current = page.url
        print(f"OAuth page: {current}")

        # Look for Continue/OK button
        try:
            continue_btn = page.query_selector('button[name="__CONFIRM__"]')
            if continue_btn:
                continue_btn.click()
                time.sleep(3)
        except:
            pass

        # Check redirect URL for token
        current = page.url
        print(f"Final URL: {current}")

        if 'access_token=' in current:
            fragment = current.split('#')[1] if '#' in current else current.split('?')[1]
            params = urllib.parse.parse_qs(fragment)
            token = params.get('access_token', [None])[0]
            if token:
                print(f"Got user token: {token[:30]}...")
                browser.close()
                return token

        # Try getting page content for debugging
        print(f"Page title: {page.title()}")
        browser.close()
        return None


def exchange_for_page_token(user_token):
    """Exchange user token for page access token"""
    print("\nGetting page access token...")

    # Get pages this user manages
    url = f'https://graph.facebook.com/v19.0/me/accounts?access_token={user_token}'
    r = requests.get(url)
    data = r.json()

    if 'data' in data and len(data['data']) > 0:
        print("Found pages:")
        for page in data['data']:
            print(f"  {page['name']} (ID: {page['id']})")
            print(f"  Page Token: {page['access_token'][:30]}...")

        # Use first page
        page = data['data'][0]
        page_token = page['access_token']
        page_id = page['id']

        # Make it a long-lived token
        print("\nExchanging for long-lived token...")
        ll_url = (
            f'https://graph.facebook.com/v19.0/oauth/access_token?'
            f'grant_type=fb_exchange_token&'
            f'client_id={app_id}&'
            f'client_secret={app_secret}&'
            f'fb_exchange_token={user_token}'
        )
        r2 = requests.get(ll_url)
        ll_data = r2.json()

        if 'access_token' in ll_data:
            ll_token = ll_data['access_token']
            # Get page token from long-lived user token
            url2 = f'https://graph.facebook.com/v19.0/me/accounts?access_token={ll_token}'
            r3 = requests.get(url2)
            pages = r3.json()
            if 'data' in pages:
                for p in pages['data']:
                    if p['id'] == page_id:
                        page_token = p['access_token']
                        print(f"Got long-lived page token!")

        return page_id, page_token
    else:
        print(f"No pages found: {data}")
        return None, None


def manual_token_flow():
    """Print instructions for manual token generation"""
    print("=" * 60)
    print("MANUAL TOKEN GENERATION")
    print("=" * 60)
    print()
    print("1. Go to: https://developers.facebook.com/tools/explorer/")
    print(f"2. Select your app: 'AI Employee' (ID: {app_id})")
    print("3. Click 'Generate Access Token'")
    print("4. Select these permissions:")
    print("   - pages_manage_posts")
    print("   - pages_read_engagement")
    print("   - pages_show_list")
    print("5. Click 'Generate Access Token' and authorize")
    print("6. Copy the token and paste it below:")
    print()

    token = input("Paste your User Access Token here: ").strip()
    if token:
        return token
    return None


if __name__ == '__main__':
    print("Facebook Token Generator")
    print("=" * 40)

    # Try Playwright first
    print("\nAttempting automated OAuth flow...")
    user_token = get_token_via_playwright()

    if not user_token:
        print("\nAutomated flow failed. Trying manual flow...")
        user_token = manual_token_flow()

    if user_token:
        # Debug the token
        debug_url = f'https://graph.facebook.com/debug_token?input_token={user_token}&access_token={app_id}|{app_secret}'
        r = requests.get(debug_url)
        print(f"\nToken debug: {r.json()}")

        page_id, page_token = exchange_for_page_token(user_token)

        if page_id and page_token:
            print(f"\n{'='*60}")
            print(f"SUCCESS! Update your .env with:")
            print(f"FACEBOOK_PAGE_ID={page_id}")
            print(f"FACEBOOK_PAGE_ACCESS_TOKEN={page_token}")
            print(f"{'='*60}")

            # Test posting
            print("\nTesting post...")
            url = f'https://graph.facebook.com/v19.0/{page_id}/feed'
            payload = {
                'message': 'Test post from AI Employee - automated!',
                'access_token': page_token
            }
            r = requests.post(url, data=payload)
            print(f"Post result: {r.status_code} - {r.json()}")
        else:
            print("\nCould not get page token. Try manual approach.")
    else:
        print("\nCould not get token. Please use Graph API Explorer manually.")
