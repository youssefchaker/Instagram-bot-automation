import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD")

# Profile Scraper Selectors
PROFILE_USERNAME_SELECTOR = "h2"
PROFILE_DISPLAY_NAME_SELECTOR = "span.x1lliihq.x1plvlek.xryxfnj.x1n2onr6.xyejjpt.x15dsfln.x193iq5w.xeuugli.x1fj9vlw.x13faqbe.x1vvkbs.x1s928wv.xhkezso.x1gmr53x.x1cpjm7i.x1fgarty.x1943h6x.x1i0vuye.xvs91rp.xo1l8bm.x5n08af.x10wh9bi.xpm28yp.x8viiok.x1o7cslx"
PROFILE_BIO_SELECTOR = "span._ap3a._aaco._aacu._aacx._aad7._aade"
PROFILE_FOLLOWERS_SELECTOR = "//a[contains(., 'followers')]/span/span"
PROFILE_FOLLOWING_SELECTOR = "//a[contains(., 'following')]/span/span"