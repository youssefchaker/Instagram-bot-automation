import schedule
import time
import random
from .browser import get_browser, login_flow
from .scraper import get_story_viewers
from .outreach import process_candidates

def job(username, password):
    """The main job to be scheduled."""
    print("Starting Instagram outreach workflow...")
    browser = None
    try:
        browser = get_browser()
        if login_flow(browser, username, password):
            story_viewers = get_story_viewers(browser, username)
            if story_viewers:
                process_candidates(browser, story_viewers)
            else:
                print("No story viewers found. Exiting.")
    except Exception as e:
        print(f"An error occurred during the workflow: {e}")
    finally:
        if browser:
            browser.quit()
    print("Workflow finished.")

def run_scheduler(username, password):
    """Runs the job once."""
    print("Scheduler started. Running the job once...")
    job(username, password)
    print("Job has finished.")
