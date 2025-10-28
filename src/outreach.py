import json
import time
import random
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        # Step 1: Navigate to user's profile
        print("Navigating to profile...")
        browser.get(f"https://www.instagram.com/{username}/")
        time.sleep(5)

        # Step 2: Click the 'Message' button
        print("Looking for the message button...")
        try:
            # Instagram has different layouts, try a few common selectors
            message_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[text()='Message']"))
            )
            message_button.click()
        except:
            # Fallback for different layouts
            message_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/direct/t/']"))
            )
            message_button.click()

        print("Message button clicked. Waiting for DM page to load...")
        time.sleep(5) # Wait for the DM page to load

        # Step 3: Send the text message
        print("Looking for the text area...")
        text_area = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Message']"))
        )
        text_area.send_keys(text)
        print("Text message sent.")
        time.sleep(2)

        # Step 4: Upload the voice note
        print("Looking for the file input...")
        # The file input is hidden, so we need to use JavaScript to interact with it
        file_input = browser.find_element(By.CSS_SELECTOR, "input[type='file']")
        
        # Get the absolute path of the file
        absolute_file_path = os.path.abspath(file_path)
        print(f"Uploading file: {absolute_file_path}")
        
        # Use JS to make the input visible and set the file
        browser.execute_script(
            "arguments[0].style.display = 'block'; " +
            "arguments[0].style.visibility = 'visible'; " +
            "arguments[0].style.height = '1px'; " +
            "arguments[0].style.width = '1px'; " +
            "arguments[0].style.opacity = 1;",
            file_input
        )
        file_input.send_keys(absolute_file_path)
        print("File input sent.")
        
        # Wait for the upload to complete and the send button to be available
        time.sleep(5)

        # Step 5: Click the send button
        print("Looking for the send button...")
        send_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Send']"))
        )
        send_button.click()
        
        print(f"Successfully sent DM to {username}")
        return True

    except Exception as e:
        print(f"An error occurred while sending DM to {username}: {e}")
        # Take a screenshot for debugging
        browser.save_screenshot(f"data/dm_error_{username}.png")
        return False