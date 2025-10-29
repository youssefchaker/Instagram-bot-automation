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
    """Loads excluded and already messaged users."""
    try:
        with open("data/excluded_usernames.txt", 'r') as f:
            excluded = [line.strip() for line in f]
    except FileNotFoundError:
        excluded = []

    try:
        with open("data/messaged_users.json", 'r') as f:
            messaged = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        messaged = []
        
    return set(excluded + messaged)

def process_candidates(browser, story_viewers):
    """Processes each candidate user."""
    exclusions = get_exclusions()
    candidates = [user for user in story_viewers if user not in exclusions]
    
    for i, username in enumerate(candidates):
        print(f"Processing candidate {i+1}/{len(candidates)}: {username}")
        
        profile_data = scrape_profile(browser, username)
        if not profile_data:
            continue

        # Save snapshot
        with open(f"data/{username}_profile.json", 'w') as f:
            json.dump(profile_data, f, indent=4)
            
        message_text = generate_message(json.dumps(profile_data, indent=4))
        if not message_text:
            continue
            
        voice_note_path = create_voice_note(message_text, username)
        
        if voice_note_path:
            send_dm(browser, username, message_text, voice_note_path)
        else:
            print(f"Skipping DM to {username} because voice note creation failed.")


        # Append to messaged users
        try:
            with open("data/messaged_users.json", 'r') as f:
                messaged_users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messaged_users = []
            
        messaged_users.append(username)
        
        with open("data/messaged_users.json", 'w') as f:
            json.dump(messaged_users, f)

        # Anti-detection delays
        if (i + 1) % 10 == 0:
            cooldown = random.randint(600, 1800) # 10-30 min cooldown
            print(f"Cooldown for {cooldown/60} minutes...")
            time.sleep(cooldown)
        else:
            delay = random.randint(60, 180) # 1-3 min delay
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
            print("Dismissed the 'Turn on Notifications' popup.")
            time.sleep(2)
        except (NoSuchElementException, TimeoutException):
            print("No 'Turn on Notifications' popup found.")
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

        # Step 4: Select the user from the results
        print("Selecting user from the list...")
        # This XPath looks for a radio button that is followed by the username, which is more robust
        user_result_radio = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[text()='{username}']/ancestor::div[@role='button']//div[@role='radio']"))
        )
        user_result_radio.click()
        time.sleep(random.uniform(1, 2))

        # Step 5: Click 'Chat' to open the conversation
        print("Clicking 'Chat' button...")
        chat_button = WebDriverWait(browser, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Chat']"))
        )
        chat_button.click()
        time.sleep(random.uniform(4, 6))


        # Step 6: Send the text message
        print("Sending text message...")
        message_input = WebDriverWait(browser, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Message']"))
        )
        message_input.send_keys(text)
        time.sleep(random.uniform(1, 2))
        
        send_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Send']"))
        )
        send_button.click()
        print("Text message sent.")
        time.sleep(random.uniform(2, 3))

        # Step 7: Upload the voice note
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
        return True

    except Exception as e:
        print(f"An error occurred while sending DM to {username}: {e}")
        browser.save_screenshot(f"data/dm_error_{username}.png")
        return False
