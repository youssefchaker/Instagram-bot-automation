import schedule
import time
import random
from src.browser import get_browser, login_flow
from src.scraper import get_story_viewers
from src.outreach import process_candidates
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

def job():
    """The main job to be scheduled."""
    print("Starting Instagram outreach workflow...")
    browser = None
    try:
        browser = get_browser()
        if login_flow(browser, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD):
            story_viewers = get_story_viewers(browser, INSTAGRAM_USERNAME)
            if story_viewers:
                process_candidates(browser, story_viewers)
    except Exception as e:
        print(f"An error occurred during the workflow: {e}")
    finally:
        if browser:
            browser.quit()
    print("Workflow finished.")

def run_scheduler():
    """Runs the scheduler."""
    print("Scheduler started. Running the job for the first time...")
    job()

    # Schedule the job every 6 hours
    schedule.every(6).hours.do(job)

    print("Job has been run once. Subsequent runs will be every 6 hours.")

    while True:
        schedule.run_pending()
        time.sleep(1)
