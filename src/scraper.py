import time
import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

def _get_viewers_for_current_story(browser):
    """Scrapes all viewers from the currently visible story."""
    time.sleep(2)
    try:
        wait = WebDriverWait(browser, 10)
        viewers_selector = "//*[contains(text(), 'Seen by')] | //*[contains(text(), 'Activity')] | //div[@role='button' and contains(., 'viewers')]"
        
        viewers_link = wait.until(EC.element_to_be_clickable((By.XPATH, viewers_selector)))
        
        print("Clicking to open the viewers list.")
        viewers_link.click()
        time.sleep(2)

    except (NoSuchElementException, TimeoutException):
        print("Could not find viewers link for the current story.")
        return set()

    try:
        scroll_container_selector = "div[style*='overflow: hidden auto']"
        scroll_container = browser.find_element(By.CSS_SELECTOR, scroll_container_selector)
        
        viewers = set()
        last_height = browser.execute_script("return arguments[0].scrollHeight", scroll_container)
        
        while True:
            username_links = scroll_container.find_elements(By.XPATH, ".//a[contains(@href, '/') and string-length(@href) > 2 and not(contains(@href, 'stories'))]")
            
            for link in username_links:
                href = link.get_attribute('href')
                if href:
                    username = href.split('/')[-2]
                    if username:
                        viewers.add(username)

            browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_container)
            time.sleep(2)

            new_height = browser.execute_script("return arguments[0].scrollHeight", scroll_container)
            if new_height == last_height:
                break
            last_height = new_height
        
        try:
            print("Closing viewers list...")
            ActionChains(browser).send_keys(Keys.ESCAPE).perform()
        except Exception as e:
            print(f"Could not close viewers list with Escape key: {e}")

        return viewers

    except Exception as e:
        print(f"An error occurred while scraping viewers for the current story: {e}")
        return set()

def get_story_viewers(browser, username):
    """Navigates to the stories and scrapes all viewers from all stories."""
    story_url = f"https://www.instagram.com/stories/{username}/"
    print("Navigating to stories...")
    browser.get(story_url)
    time.sleep(1)

    if f"/stories/" not in browser.current_url:
        print("No stories available for this user.")
        return []

    all_viewers = set()
    story_index = 1

    # Loop as long as we are in the story view
    while f"/stories/" in browser.current_url:
        print(f"Processing story {story_index}...")

        current_viewers = _get_viewers_for_current_story(browser)
        if current_viewers:
            all_viewers.update(current_viewers)
            print(f"Found {len(current_viewers)} viewers for this story. Total unique viewers so far: {len(all_viewers)}")
        else:
            print("No viewers found for this story.")

        # Check if we are still in stories before advancing
        if f"/stories/" not in browser.current_url:
            print("Exited story after scraping.")
            break

        print("Advancing to next story...")
        ActionChains(browser).send_keys(Keys.ARROW_RIGHT).perform()
        time.sleep(1)
        story_index += 1

    print(f"Finished processing all stories. Found a total of {len(all_viewers)} viewers.")
    return list(all_viewers)

def scrape_profile(browser, username):
    """Scrapes signals from a user's profile."""
    browser.get(f"https://www.instagram.com/{username}/")
    time.sleep(2)

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