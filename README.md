# Instagram Story Viewer Outreach Bot

This bot automates the process of reaching out to Instagram users who have viewed your stories.

## Features

- Automated login and session handling
- Scheduled execution every 6 hours
- Scrapes story viewers
- Filters users based on exclusion lists
- Scrapes user profiles for personalization
- Generates personalized messages using OpenAI
- Creates voice notes using ElevenLabs
- Sends DMs with text and voice notes
- Implements anti-detection measures

## Setup

1.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Add your API keys to `config.py`.
3.  Add usernames to `data/excluded_usernames.txt` that you want to exclude from the outreach.
4.  Run the bot:
    ```bash
    python main.py
    ```
