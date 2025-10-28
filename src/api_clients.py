from openai import OpenAI
import requests
from config import OPENAI_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_message(profile_json):
    """Generates a personalized message using OpenAI."""
    prompt = f"""
    Based on the following user profile data, generate a friendly 3-4 line intro text.
    Acknowledge that I saw them in my story viewers, add one small personal touch based on their profile, and have a soft, friendly closing question.
    Keep it casual and not salesy.

    Profile Data:
    {profile_json}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly assistant helping me write a casual outreach message."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating message with OpenAI: {e}")
        return None

def create_voice_note(text, username):
    """Creates a voice note using ElevenLabs API."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            file_path = f"data/{username}_voice_note.mp3"
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Voice note for {username} saved to {file_path}")
            return file_path
        else:
            print(f"Error from ElevenLabs API: {response.text}")
            return None
    except Exception as e:
        print(f"Error creating voice note: {e}")
        return None