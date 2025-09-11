import os
import re
import io
import requests
from collections import Counter
from PIL import Image
from dotenv import load_dotenv

from transformers import pipeline
import tweepy
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))

load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")  # RapidAPI key if available
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")  # Google API key as fallback
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "youtube-v31.p.rapidapi.com")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


twitter_client = None
if BEARER_TOKEN:
    try:
        twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)
        print("[INFO] Twitter client initialized.")
    except Exception as e:
        print(f"[ERROR] Twitter client failed: {e}")
        twitter_client = None


try:
    import torch
    DEVICE = 0 if torch.cuda.is_available() else -1
except Exception:
    DEVICE = -1
print(f"[INFO] Device set to {'GPU' if DEVICE == 0 else 'CPU'}")


print("[INFO] Loading ML pipelines... This may take some time on first run.")

def init_pipelines():
    sentiment = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english", revision="714eb0f", device=DEVICE)
    print("[INFO] Sentiment pipeline loaded.")
    zero_shot = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=DEVICE)
    print("[INFO] Zero-shot pipeline loaded.")
    image_clf = pipeline("image-classification", model="google/vit-base-patch16-224", revision="3f49326", device=DEVICE)
    print("[INFO] Image classification pipeline loaded.")
    return sentiment, zero_shot, image_clf

sentiment_pipeline, zero_shot_pipeline, image_pipeline = init_pipelines()


HAZARD_WEIGHTS = {
    "tsunami":10,"earthquake":10,"cyclone":9,"hurricane":9,"volcano":9,"eruption":9,"wildfire":9,
    "flood":8,"flooding":8,"landslide":8,"mudslide":8,"avalanche":8,"storm":7,"typhoon":7,"surge":7,
    "tornado":6,"drought":6,"heatwave":6,"hailstorm":5,"snowstorm":5,"inundation":5,
    "wave":3,"waves":3,"coast":2,"shore":2,"sea":2,"rain":2,"wind":2,"high":1,"water":1
}

IMAGE_HAZARD_KEYWORDS = [
    "flood","storm","cyclone","hurricane","tsunami","wave","waves","surge","sea","ocean","river","coast","shore",
    "wreck","ruin","collapse","broken","destruction","damaged","debris","mud","landslide","avalanche","rockfall",
    "drought","fire","wildfire","smoke","ash","eruption","storm-cloud","thunderstorm","hail","snowstorm",
    "boat","shipwreck","rescue","evacuation","people","crowd","shelter","tent","emergency","ambulance"
]


MOCK_TWEETS = [
    {"text":"Huge tsunami warning issued for coastal areas!","media_urls":[]},
    {"text":"Massive storm surge expected tonight, stay safe!","media_urls":[]}
]

MOCK_YT_VIDEOS = [
    {"title":"Tsunami Alert in Coastal Areas","description":"Authorities warn residents...","thumbnail":"","video_url":"https://youtu.be/mock1"},
    {"title":"Flooded Streets After Storm","description":"Heavy rainfall caused flooding...","thumbnail":"","video_url":"https://youtu.be/mock2"}
]


def clean_text(t):
    t = re.sub(r"http\S+"," ",t)
    t = re.sub(r"[^A-Za-z0-9\s]"," ",t)
    t = re.sub(r"\s+"," ",t).strip()
    return t.lower()

def calculate_text_hazard_score(text):
    text_l = clean_text(text)
    score = 0
    for kw, weight in HAZARD_WEIGHTS.items():
        score += len(re.findall(rf"\b{re.escape(kw)}\b", text_l)) * weight
    urgency = text.count("!") + sum(1 for w in text.split() if w.isupper() and len(w)>1)
    score += min(urgency*1.5,4)
    return float(score)

def fetch_tweets_with_media(keywords):
    if not twitter_client:
        print("[WARN] No Twitter API key found, using mock tweets.")
        return MOCK_TWEETS
    try:
        print("[INFO] Attempting to fetch live tweets...")
        
        return MOCK_TWEETS  
    except Exception as e:
        print(f"[ERROR] Twitter API failed: {e}, using mock tweets.")
        return MOCK_TWEETS

def fetch_youtube_videos(keywords):
    # Try RapidAPI first
    if RAPIDAPI_KEY:
        try:
            print(f"[INFO] Attempting to fetch YouTube videos via RapidAPI (Host: {RAPIDAPI_HOST})...")
            url = f"https://{RAPIDAPI_HOST}/search"
            headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}
            params = {"q": ' OR '.join(keywords), "part": "snippet", "maxResults":5, "order": "date", "type": "video"}
            res = requests.get(url, headers=headers, params=params, timeout=8)
            res.raise_for_status()
            data = res.json()
            videos = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                videos.append({
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "video_url": f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId', '')}"
                })
            return videos or MOCK_YT_VIDEOS
        except requests.exceptions.HTTPError as e:
            print(f"[ERROR] YouTube RapidAPI HTTPError: {e.response.status_code} - {e.response.text}, trying Google API...")
        except Exception as e:
            print(f"[ERROR] YouTube RapidAPI failed: {e}, trying Google API...")

        try:
            print("[INFO] Attempting to fetch YouTube videos via Google API key...")
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {"key": YOUTUBE_API_KEY, "q": ' OR '.join(keywords), "part": "snippet", "maxResults":5, "order": "date", "type": "video"}
            res = requests.get(url, params=params, timeout=8)
            res.raise_for_status()
            data = res.json()
            videos = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                videos.append({
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url"),
                    "video_url": f"https://www.youtube.com/watch?v={item.get('id', {}).get('videoId', '')}"
                })
            return videos or MOCK_YT_VIDEOS
        except Exception as e:
            print(f"[ERROR] YouTube Google API failed: {e}, using mock videos.")

    print("[WARN] No API key available, using mock YouTube videos.")
    return MOCK_YT_VIDEOS


if __name__ == "__main__":
    keywords = ["tsunami","flood","cyclone"]

    print("[INFO] Fetching tweets...")
    tweets = fetch_tweets_with_media(keywords)

    print("[INFO] Fetching YouTube videos...")
    youtube_videos = fetch_youtube_videos(keywords)

    print("\n[INFO] Hazard Report Summary")
    print("Keywords:", keywords)
    print("Tweets fetched:", len(tweets))
    for t in tweets:
        print(" -", t['text'])

    print("YouTube videos fetched:", len(youtube_videos))
    for v in youtube_videos:
        print(f" - {v['title']} ({v['video_url']})")

    
    avg_score = sum(calculate_text_hazard_score(t['text']) for t in tweets)/len(tweets)
    overall_risk = 'High' if avg_score>=6 else 'Medium' if avg_score>=3 else 'Low'
    print(f"Average Hazard Score: {avg_score:.2f}, Overall Risk: {overall_risk}")