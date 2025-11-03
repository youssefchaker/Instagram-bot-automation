import requests


def generate_message(profile_json):
    """Generates a personalized message using Pollinations.AI."""
    prompt = f"""
    Based on the following user profile data, generate a friendly 3-4 line intro text.
    Acknowledge that I saw them in my story viewers, add one small personal touch based on their profile, and have a soft, friendly closing question.
    Keep it casual and not salesy and do not appear creepy or stalky(do not mention the number of followers or any specific details that would indicate deep stalking).

    Profile Data:
    {profile_json}
    """
    
    url = "https://text.pollinations.ai/"
    headers = {"Content-Type": "application/json"}
    data = {
        "messages": [
            {"role": "system", "content": "You are a friendly assistant helping me write a casual outreach message."},
            {"role": "user", "content": prompt}
        ],
        "model": "openai",
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error generating message with Pollinations.AI: {e}")
        return None

from gtts import gTTS

def create_voice_note(text, username):
    """Creates a voice note using the gTTS library."""
    try:
        tts = gTTS(text=text, lang='en')
        file_path = f"data/{username}_voice_note.mp3"
        tts.save(file_path)
        print(f"Voice note for {username} saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error creating voice note with gTTS: {e}")
        return None