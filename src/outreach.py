import json
import time
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from src.scraper import scrape_profile
from src.api_clients import generate_message, create_voice_note

def get_exclusions():
    """Loads excluded and already scraped users."""
    try:
        with open("data/excluded_usernames.txt", 'r') as f:
            excluded = [line.strip() for line in f]
    except FileNotFoundError:
        excluded = []

    try:
        with open("data/scraped_users.json", 'r') as f:
            scraped_users = json.load(f)
            scraped_usernames = [user['username'] for user in scraped_users]
    except (FileNotFoundError, json.JSONDecodeError):
        scraped_usernames = []

    return set(excluded + scraped_usernames)

def process_candidates(browser, story_viewers):
    """Processes each candidate user."""
    exclusions = get_exclusions()
    candidates = [user for user in story_viewers if user not in exclusions]

    try:
        with open("data/scraped_users.json", 'r') as f:
            scraped_users = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        scraped_users = []

    for i, username in enumerate(candidates):
        print(f"Processing candidate {i+1}/{len(candidates)}: {username}")

        profile_data = scrape_profile(browser, username)
        if not profile_data:
            continue

        scraped_users.append(profile_data)

        with open("data/scraped_users.json", 'w') as f:
            json.dump(scraped_users, f, indent=4)

        message_text = generate_message(json.dumps(profile_data, indent=4))
        if not message_text:
            continue

        voice_note_path = create_voice_note(message_text, username)

        if voice_note_path:
            if send_dm(browser, username, message_text, voice_note_path):
                try:
                    os.remove(voice_note_path)
                    print(f"Deleted local voice note: {voice_note_path}")
                except OSError as e:
                    print(f"Error deleting voice note file {voice_note_path}: {e}")
            else:
                print(f"Skipping DM to {username} because sending failed.")
        else:
            print(f"Skipping DM to {username} because voice note creation failed.")


        # Anti-detection delays
        if i < len(candidates) - 1:
            if (i + 1) % 10 == 0:
                cooldown = random.randint(600, 1800)
                print(f"Cooldown for {cooldown/60} minutes...")
                time.sleep(cooldown)
            else:
                delay = random.randint(60, 180)
                print(f"Waiting for {delay} seconds before processing the next candidate...")
                time.sleep(delay)

def send_dm(browser, username, text, file_path):
    """Sends a DM with text and a voice note."""
    print(f"Attempting to send DM to {username}...")
    try:
        # Step 1: Navigate to messages
        print("Navigating to messages...")
        messages_link = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, '/direct/inbox/')]"))
        )
        messages_link.click()
        time.sleep(random.uniform(3, 5))

        # Handle 'Turn on Notifications' popup
        try:
            not_now_button = WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
            )
            not_now_button.click()
            print("Dismissed the notifications popup.")
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            print("No notifications popup found.")
            pass

        # Step 2: Click on the 'New Message' button to open the search modal
        print("Clicking on 'New Message' button...")
        new_message_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//div[text()='New message']] | //div[contains(text(),'Send message')]"))
        )
        new_message_button.click()
        time.sleep(random.uniform(2, 3))


        # Step 3: Find the search bar and search for the user
        print(f"Searching for user '{username}'...")
        search_input = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search...']"))
        )
        search_input.send_keys(username)
        time.sleep(random.uniform(2, 4))

        # Step 4: Select the first user from the results
        print("Selecting the first user from the list...")
        first_user_result = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "(//div[@role='button' and .//input[@name='ContactSearchResultCheckbox']])[1]"))
        )
        first_user_result.click()
        time.sleep(random.uniform(1, 2))

        # Step 5: Click 'Chat' to open the conversation
        print("Clicking 'Chat' button...")
        chat_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Chat']"))
        )
        chat_button.click()
        time.sleep(random.uniform(4, 6))

        # Step 6: Upload the voice note
        print("Uploading voice note...")
        file_input = browser.find_element(By.XPATH, "//input[@type='file']")
        absolute_file_path = os.path.abspath(file_path)
        
        browser.execute_script(
            "arguments[0].style.display = 'block'; arguments[0].style.visibility = 'visible';",
            file_input
        )
        file_input.send_keys(absolute_file_path)
        time.sleep(random.uniform(3, 5)) # Wait for upload

        # After uploading, a send button for the attachment appears
        print("Sending voice note...")
        send_attachment_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Send']"))
        )
        send_attachment_button.click()
        time.sleep(random.uniform(3, 5))

        print(f"Successfully sent DM to {username}")
        
        # Navigate back to home page to be ready for the next user
        print("Navigating back to home page...")
        browser.get("https://www.instagram.com/")
        time.sleep(random.uniform(3, 5))

        return True

    except Exception as e:
        print(f"An error occurred while sending DM to {username}: {e}")
        browser.save_screenshot(f"data/dm_error_{username}.png")

        # Also navigate back to home page on error to try to recover
        print("Navigating back to home page after error...")
        browser.get("https://www.instagram.com/")
        time.sleep(random.uniform(3, 5))
        
        return False
