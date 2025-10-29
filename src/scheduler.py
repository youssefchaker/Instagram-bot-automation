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
    except Exception as e:
        print(f"An error occurred during the workflow: {e}")
    finally:
        if browser:
            browser.quit()
    print("Workflow finished.")

def run_scheduler(username, password):
    """Runs the scheduler."""
    print("Scheduler started. Running the job for the first time...")
    job(username, password)

    # Schedule the job every 6 hours
    schedule.every(6).hours.do(job, username, password)

    print("Job has been run once. Subsequent runs will be every 6 hours.")

    while True:
        schedule.run_pending()
        time.sleep(1)
