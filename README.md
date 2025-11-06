# Instagram Outreach Bot

This project is an Instagram automation bot designed to streamline outreach efforts. It identifies users who have viewed your stories, scrapes their profile information, and sends them personalized direct messages, including a voice note. The bot comes with a Django-based web dashboard to monitor and control the outreach process.

## Features

- **Story Viewer Scraping:** Automatically scrapes the usernames of users who have viewed your Instagram stories.
- **Profile Scraping:** Gathers key information from user profiles, including display name, bio, follower count, and following count.
- **AI-Powered Personalization:** Generates unique, personalized messages for each user based on their profile data.
- **Voice Note Generation:** Converts the personalized text messages into voice notes for a more personal touch.
- **Automated DMs:** Sends the personalized message and voice note directly to the target user's inbox.
- **Exclusion Lists:** Maintains a list of users who have already been contacted or should be excluded from outreach.
- **Web Dashboard:** A user-friendly interface to:
    - Log in with your Instagram credentials.
    - View a table of all scraped users and their profile details.
    - Manually trigger the outreach process.
    - Remove individual users from the outreach list.
    - Clear the entire list of scraped users.

## Project Structure

```
├── dashboard/         # Django web dashboard
│   ├── outreach/      # Django app for outreach management
│   ├── manage.py      # Django management script
├── data/              # Data files (e.g., scraped users)
├── src/               # Source code for the bot
│   ├── api_clients.py # Handles API calls for message generation
│   ├── browser.py     # Manages the Selenium browser instance
│   ├── outreach.py    # Core outreach logic
│   ├── scheduler.py   # Schedules bot execution
│   └── scraper.py     # Handles scraping of story viewers and profiles
├── config.py          # Configuration settings and selectors
├── main.py            # Main entry point for the bot
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/instagram-bot-automation.git
   cd instagram-bot-automation
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv insta-bot-venv
   source insta-bot-venv/bin/activate  # On Windows, use `insta-bot-venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

You can run the bot directly from the command line or use the web dashboard for more control.

### Running the Bot Directly

To run the outreach process immediately, execute the `main.py` script:

```bash
python main.py
```

### Using the Web Dashboard

1. **Start the Django development server:**
   ```bash
   cd dashboard
   python manage.py runserver
   ```

2. **Access the dashboard:**
   Open your web browser and navigate to `http://127.0.0.1:8000/`.

3. **Log in:**
   You will be prompted to enter your Instagram username and password. These credentials are used to authenticate with Instagram and perform the outreach actions.

4. **Manage outreach:**
   From the dashboard, you can:
   - Click **Run Outreach Process** to start the scraping and messaging sequence.
   - View all scraped users in the table.
   - **Remove** specific users from the list.
   - **Clear All Users** to reset the outreach list.
   - **Logout** to clear your session and credentials.

## Configuration

The `config.py` file contains selectors used for scraping Instagram. These may need to be updated if Instagram changes its website structure.

## Dependencies

The main dependencies for this project are:

- `selenium`: For browser automation and web scraping.
- `requests`: For making HTTP requests to APIs.
- `schedule`: For scheduling jobs.
- `python-dotenv`: For managing environment variables.
- `gTTS`: For generating voice notes from text.
- `Django`: For the web dashboard.
- `django-crispy-forms`: For styling Django forms.
- `crispy-bootstrap5`: For using Bootstrap 5 with crispy-forms.
