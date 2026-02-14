#!/usr/bin/env python3
"""
Twitter Selenium Poster - Using Selenium WebDriver
"""
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

load_dotenv()

def post_to_twitter_selenium(content: str):
    """Post to Twitter using Selenium"""

    email = os.getenv('TWITTER_EMAIL')
    password = os.getenv('TWITTER_PASSWORD')

    if not email or not password:
        print("❌ TWITTER_EMAIL and TWITTER_PASSWORD not set")
        return False

    print(f"🐦 Twitter Selenium Posting")
    print(f"Account: {email}")
    print(f"Content: {content[:80]}...")

    try:
        # Setup Chrome options
        chrome_options = Options()

        # Don't use headless - makes it more detectable
        # chrome_options.add_argument("--headless")

        # Mimic real browser
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        print("🔧 Starting Chrome...")
        driver = webdriver.Chrome(options=chrome_options)

        # Go to Twitter
        print("🌐 Opening Twitter...")
        driver.get("https://twitter.com/home")
        time.sleep(3)

        # Check if login needed
        if "login" in driver.current_url or "authorize" in driver.current_url:
            print("🔑 Logging in...")

            # Email
            try:
                email_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]'))
                )
                email_input.send_keys(email)
                time.sleep(1)

                # Click Next
                driver.find_element(By.XPATH, "//button[contains(., 'Next')]").click()
                time.sleep(1)

                # Password
                password_input = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="password"]'))
                )
                password_input.send_keys(password)
                time.sleep(1)

                # Click Login
                driver.find_element(By.XPATH, "//button[contains(., 'Log in')]").click()

                print("⏳ Waiting for feed...")
                time.sleep(5)
            except Exception as e:
                print(f"❌ Login failed: {e}")
                driver.quit()
                return False

        print("✍️ Opening compose...")

        # Press 'c' to compose
        driver.find_element(By.TAG_NAME, "body").send_keys("c")
        time.sleep(2)

        print("📝 Typing tweet...")

        # Find tweet text area
        try:
            tweet_area = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[role="textbox"]'))
            )
            tweet_area.send_keys(content)
            time.sleep(1)
        except Exception as e:
            print(f"❌ Could not find tweet area: {e}")
            driver.quit()
            return False

        print("📤 Posting...")

        # Click Post button
        try:
            post_button = driver.find_element(By.XPATH, "//button[contains(., 'Post')]")
            post_button.click()
            time.sleep(3)

            print("✅ Tweet posted! 🎉")
            driver.quit()
            return True
        except Exception as e:
            print(f"❌ Could not click Post: {e}")
            driver.quit()
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

    success = post_to_twitter_selenium(content)
    sys.exit(0 if success else 1)
