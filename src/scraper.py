import time
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_story_viewers(browser, username):
    """Navigates to the story and scrapes all viewers from the story viewers list."""
    try:
        # Navigate directly to the user's stories
        story_url = f"https://www.instagram.com/stories/{username}/"
        print(f"Navigating to stories at {story_url}...")
        browser.get(story_url)
        
        wait = WebDriverWait(browser, 15)

        # Wait for the story to load and find the viewers link at the bottom.
        viewers_selector = "//*[contains(text(), 'Seen by')] | //*[contains(text(), 'Activity')] | //div[@role='button' and contains(., 'viewers')]"
        
        viewers_link = wait.until(EC.element_to_be_clickable((By.XPATH, viewers_selector)))
        
        print("Found viewers link/area. Clicking to open the viewers list.")
        viewers_link.click()
        time.sleep(3)

    except (NoSuchElementException, TimeoutException):
        print("No active story found, or the viewers link could not be located.")
        try:
            browser.find_element(By.XPATH, "//*[contains(text(), 'No viewers yet')]")
            print("Story has no viewers yet.")
        except NoSuchElementException:
            pass
        return []
    except Exception as e:
        print(f"An unexpected error occurred while trying to navigate to story viewers: {e}")
        return []

    # Now that the viewers list is open, proceed with scraping
    try:
        print("Looking for the story viewers list scroll container...")
        scroll_container_selector = "div[style*='overflow: hidden auto']"
        scroll_container = browser.find_element(By.CSS_SELECTOR, scroll_container_selector)
        print("Found the scrollable container.")

        viewers = set()
        last_height = browser.execute_script("return arguments[0].scrollHeight", scroll_container)
        
        print("Scrolling to load all viewers...")
        while True:
            # Find all usernames currently visible
            username_links = scroll_container.find_elements(By.XPATH, ".//a[contains(@href, '/') and string-length(@href) > 2 and not(contains(@href, 'stories'))]")
            
            for link in username_links:
                href = link.get_attribute('href')
                if href:
                    username = href.split('/')[-2]
                    if username:
                        viewers.add(username)

            browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
            time.sleep(2)

            # Check if we've reached the bottom
            new_height = browser.execute_script("return arguments[0].scrollHeight", scroll_container)
            if new_height == last_height:
                break
            last_height = new_height
        
        print(f"Found {len(viewers)} unique story viewers.")
        return list(viewers)

    except Exception as e:
        print(f"An error occurred while scraping story viewers: {e}")
        return []

def scrape_profile(browser, username):
    """Scrapes signals from a user's profile."""
    browser.get(f"https://www.instagram.com/{username}/")
    time.sleep(5)

    profile_data = {"username": username}
    
    # Scrape user_id
    try:
        page_source = browser.page_source
        user_id_match = re.search(r'"profilePage_(\d+)"', page_source)
        if user_id_match:
            profile_data["user_id"] = user_id_match.group(1)
        else:
            profile_data["user_id"] = None
            print(f"Could not find user_id for {username}.")
    except Exception as e:
        profile_data["user_id"] = None
        print(f"An error occurred while scraping user_id for {username}: {e}")

    # Scrape display name
    try:
        display_name_element = browser.find_element(By.CSS_SELECTOR, "h2")
        profile_data["display_name"] = display_name_element.text
    except NoSuchElementException:
        profile_data["display_name"] = ""
        print(f"Could not find display name for {username}.")

    # Scrape bio
    try:
        bio_element = browser.find_element(By.CSS_SELECTOR, "span._ap3a._aaco._aacu._aacx._aad7._aade")
        profile_data["bio"] = bio_element.text
    except NoSuchElementException:
        profile_data["bio"] = ""
        print(f"Could not find bio for {username}.")

    # Scrape followers and following counts
    try:
        follower_link = browser.find_element(By.XPATH, "//a[contains(., 'followers')]")
        
        try:
            followers_count_span = follower_link.find_element(By.XPATH, ".//span[@title]")
            followers_count = followers_count_span.get_attribute("title")
        except NoSuchElementException:
            followers_count = follower_link.text.split(' ')[0]

        profile_data["followers"] = int(followers_count.replace(',', ''))

    except (NoSuchElementException, ValueError):
        profile_data["followers"] = 0
        print(f"Could not parse followers count for {username}.")

    try:
        following_link = browser.find_element(By.XPATH, "//a[contains(., 'following')]")
        following_count = following_link.text.split(' ')[0]
        profile_data["following"] = int(following_count.replace(',', ''))
    except (NoSuchElementException, ValueError):
        profile_data["following"] = 0
        print(f"Could not parse following count for {username}.")


    print(f"Successfully scraped profile for {username}: {profile_data}")
    return profile_data