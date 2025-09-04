import os
import re
import io
import requests
import pandas as pd
from wordcloud import WordCloud
from dotenv import load_dotenv
from PIL import Image
from collections import Counter


from transformers import pipeline
import tweepy


import nltk
from nltk.corpus import stopwords

nltk.download('stopwords', quiet=True)
STOPWORDS = set(stopwords.words('english'))


load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")


twitter_client = None
if BEARER_TOKEN:
    try:
        twitter_client = tweepy.Client(
            bearer_token=BEARER_TOKEN, wait_on_rate_limit=True
        )
    except Exception:
        twitter_client = None


try:
    import torch
    DEVICE = 0 if torch.cuda.is_available() else -1
except Exception:
    DEVICE = -1


def init_pipelines():
    sentiment = pipeline("sentiment-analysis", device=DEVICE)
    zero_shot = pipeline(
        "zero-shot-classification",
        model="cardiffnlp/twitter-roberta-base-sentiment",
        device=DEVICE,
    )
    image_clf = pipeline("image-classification", device=DEVICE)
    return sentiment, zero_shot, image_clf

sentiment_pipeline, zero_shot_pipeline, image_pipeline = init_pipelines()


HAZARD_WEIGHTS = {
    # 🔴 Critical Hazards (High Fatality / Sudden Onset)
    "tsunami": 10,
    "earthquake": 10,
    "cyclone": 9,
    "hurricane": 9,
    "volcano": 9,
    "eruption": 9,
    "wildfire": 9,
    
    # 🟠 Severe Hazards (Regional Damage, Strong Warnings)
    "flood": 8,
    "flooding": 8,
    "landslide": 8,
    "mudslide": 8,
    "avalanche": 8,
    "storm": 7,
    "typhoon": 7,
    "surge": 7,
    
    # 🟡 Medium Hazards (Localized / Manageable Risks)
    "tornado": 6,
    "drought": 6,
    "heatwave": 6,
    "hailstorm": 5,
    "snowstorm": 5,
    "inundation": 5,
    
    # 🟢 Lower-Weight Contextual Keywords (indicators but not direct hazards)
    "wave": 3,
    "waves": 3,
    "coast": 2,
    "shore": 2,
    "sea": 2,
    "rain": 2,
    "wind": 2,
    "high": 1,
    "water": 1
}


HIGH_SEVERITY_KEYWORDS = {
    "tsunami", "earthquake", "cyclone", "hurricane", "volcano", "eruption",
    "wildfire", "flood", "flooding", "landslide", "mudslide", "avalanche"
}


IMAGE_HAZARD_KEYWORDS = [
    # Water-related hazards
    "flood", "storm", "cyclone", "hurricane", "tsunami", "wave", "waves",
    "surge", "sea", "ocean", "river", "coast", "shore", "harbor", "pier",
    
    # Damage indicators
    "wreck", "ruin", "collapse", "broken", "destruction", "damaged",
    "debris", "mud", "landslide", "avalanche", "rockfall",
    
    # Environment / human impact
    "drought", "fire", "wildfire", "smoke", "ash", "eruption",
    "storm-cloud", "thunderstorm", "hail", "snowstorm",
    
    # Secondary objects that imply hazard impact
    "boat", "shipwreck", "rescue", "evacuation", "people", "crowd",
    "shelter", "tent", "emergency", "ambulance"
]



def clean_text(t: str):
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"[^A-Za-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t.lower()

def extract_keywords_from_texts(texts, top_n=15):
    all_words = []
    for t in texts:
        for w in clean_text(t).split():
            if w not in STOPWORDS and len(w) > 2:
                all_words.append(w)
    return [w for w, _ in Counter(all_words).most_common(top_n)]


def calculate_text_hazard_score(text):
    text_l = clean_text(text)
    score = 0
    for kw, weight in HAZARD_WEIGHTS.items():
        matches = len(re.findall(rf"\b{re.escape(kw)}\b", text_l))
        score += matches * weight
    urgency = text.count("!") + sum(1 for w in text.split() if w.isupper() and len(w) > 1)
    score += min(urgency * 1.5, 4)
    return float(score)

def risk_from_score(score):
    if score >= 6:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"

def calculate_image_hazard_score(pil_image):
    try:
        results = image_pipeline(pil_image, top_k=5)
    except Exception:
        return 0.0, []
    score = 0.0
    matched_labels = []
    for r in results:
        label = r.get("label", "").lower()
        conf = float(r.get("score", 0.0))
        for key in IMAGE_HAZARD_KEYWORDS:
            if key in label:
                score += conf * 5.0
                matched_labels.append((label, conf))
                break
    score = min(score, 5.0)
    return float(round(score, 3)), matched_labels

def fuse_scores(text_score, image_score, image_confident=False):
    text_norm = min(text_score / 10.0, 1.0)
    image_norm = min(image_score / 5.0, 1.0)
    if image_confident and image_score >= 3.5:
        w_image, w_text = 0.6, 0.4
    else:
        w_image, w_text = 0.4, 0.6
    fused = w_text * text_norm + w_image * image_norm
    return float(round(fused * 10, 3)), {
        "text_norm": text_norm,
        "image_norm": image_norm,
        "w_text": w_text,
        "w_image": w_image,
    }


def fetch_tweets_with_media(keywords, max_results=20):
    if not twitter_client:
        return []
    query = "(" + " OR ".join(keywords) + ") -is:retweet lang:en"
    try:
        resp = twitter_client.search_recent_tweets(
            query=query,
            max_results=max_results,
            expansions=["attachments.media_keys"],
            media_fields=["url", "preview_image_url", "type"],
        )
    except Exception:
        return []
    tweets, includes = [], resp.includes or {}
    media_map = {}
    if "media" in includes:
        for m in includes["media"]:
            key = getattr(m, "media_key", None)
            url = getattr(m, "url", None) or getattr(m, "preview_image_url", None)
            if key and url:
                media_map[key] = url
    if resp.data:
        for t in resp.data:
            text, m_urls = t.text, []
            if hasattr(t, "attachments") and getattr(t.attachments, "media_keys", None):
                for mk in t.attachments.media_keys:
                    if mk in media_map:
                        m_urls.append(media_map[mk])
            tweets.append({"text": text, "media_urls": m_urls})
    return tweets

def download_image_from_url(url):
    try:
        r = requests.get(url, timeout=8)
        return Image.open(io.BytesIO(r.content)).convert("RGB")
    except Exception:
        return None

# --- Mock Data (offline demo) ---
MOCK_TWEETS = [
    {"text": "Huge tsunami warning issued for coastal areas!", "media_urls": []},
    {"text": "Massive storm surge expected tonight, stay safe!", "media_urls": []},
    {"text": "Cyclone approaching, authorities on high alert!", "media_urls": []},
    {"text": "Flood waters rising fast, avoid low-lying areas!", "media_urls": []},
    {"text": "High waves reported along the coast, surfing dangerous!", "media_urls": []},
]
