import time
from src.scheduler import run_scheduler
from config import INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD

if __name__ == "__main__":
    run_scheduler(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
