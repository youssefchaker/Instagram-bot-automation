from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json

def get_browser():
    """Initializes and returns a Selenium browser instance."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return browser

def login(browser, username, password):
    """Handles Instagram login."""
    browser.get("https://www.instagram.com/accounts/login/")
    time.sleep(3)
    
    # Find username and password fields and enter credentials
    username_input = browser.find_element("name", "username")
    password_input = browser.find_element("name", "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    
    # Click login button
    login_button = browser.find_element("xpath", "//*[@id='loginForm']/div/div[3]/button")
    login_button.click()
    time.sleep(3)

def handle_popups(browser):
    """Handles common pop-ups after login by trying a list of selectors."""
    time.sleep(1) # Wait for popups
    selector="//div[@role='button' and text()='OK']"
    try:
        element = browser.find_element("xpath", selector)
        element.click()
        print(f"Clicked element with selector: {selector}")
        time.sleep(2)
    except:
        pass

def save_cookies(browser, path="data/cookies.json"):
    """Saves browser cookies to a file."""
    if not os.path.exists("data"):
        os.makedirs("data")
    with open(path, 'w') as f:
        json.dump(browser.get_cookies(), f)

def load_cookies(browser, path="data/cookies.json"):
    """Loads browser cookies from a file."""
    if os.path.exists(path):
        with open(path, 'r') as f:
            cookies = json.load(f)
        for cookie in cookies:
            browser.add_cookie(cookie)
        return True
    return False

def login_flow(browser, username, password):
    """Manages the full login flow, using cookies if available."""
    browser.get("https://www.instagram.com")
    if not load_cookies(browser):
        print("Cookies not found, proceeding with manual login.")
        login(browser, username, password)
        save_cookies(browser)
    else:
        print("Cookies loaded successfully.")
        browser.refresh()
        time.sleep(5)

    handle_popups(browser)

    # Verify login by checking for profile picture
    try:
        browser.find_element("xpath", f"//a[contains(@href, '/{username}/')]")
        print("Login successful.")
        return True
    except:
        print("Login failed. Please check your credentials or complete manual login steps.")
        # If cookie login fails, attempt manual login
        login(browser, username, password)
        save_cookies(browser)
        browser.get("https://www.instagram.com")
        time.sleep(5)
        handle_popups(browser)
        try:
            browser.find_element("xpath", f"//a[contains(@href, '/{username}/')]")
            print("Login successful after second attempt.")
            return True
        except:
            print("Login failed again. Exiting.")
            return False