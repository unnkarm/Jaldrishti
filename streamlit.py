# app_multimodal_hazard.py
import os
import re
import io
import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from dotenv import load_dotenv
from PIL import Image
from collections import Counter

# NLP and multimodal models
from transformers import pipeline, AutoFeatureExtractor, AutoModelForImageClassification

# Optional Twitter v2 client
import tweepy

# NLTK for stopwords (optional for keyword extraction)
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')
STOPWORDS = set(stopwords.words('english'))

# Load env
load_dotenv()
BEARER_TOKEN = os.getenv("BEARER_TOKEN")

# Attempt to initialize Twitter client if token present
twitter_client = None
if BEARER_TOKEN:
    try:
        twitter_client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)
    except Exception as e:
        twitter_client = None
        st.warning(f"Twitter client init failed: {e}")

# Device selection for transformers/pytorch: use GPU if available
try:
    import torch
    DEVICE = 0 if torch.cuda.is_available() else -1  # pipeline device param: 0 for gpu, -1 for cpu
except Exception:
    DEVICE = -1

# Initialize transformers pipelines (with device)
@st.cache_resource(show_spinner=False)
def init_pipelines():
    # text sentiment (fast)
    sentiment = pipeline("sentiment-analysis", device=DEVICE)
    # zero-shot for hazard classification (text)
    zero_shot = pipeline("zero-shot-classification", model="cardiffnlp/twitter-roberta-base-sentiment", device=DEVICE)
    # image classification (uses a vision model via transformers)
    # Use a general image-classification pipeline (will pick a reasonable ViT/ResNet under the hood)
    image_clf = pipeline("image-classification", device=DEVICE)
    return sentiment, zero_shot, image_clf

sentiment_pipeline, zero_shot_pipeline, image_pipeline = init_pipelines()

# Hazard keyword weights (optimized)
HAZARD_WEIGHTS = {
    "tsunami": 5,
    "earthquake": 5,
    "cyclone": 4,
    "flood": 4,
    "storm": 3,
    "surge": 2,
    "high": 1,
    "wave": 1,
    "waves": 1,
    "coast": 2,
    "flooding": 4,
    "inundation": 4
}

# Keywords considered high-severity for boosting
HIGH_SEVERITY_KEYWORDS = {"tsunami", "earthquake", "cyclone", "flood", "flooding"}

# Image label keywords mapping (labels returned by image pipeline that indicate hazard)
IMAGE_HAZARD_KEYWORDS = ["flood", "storm", "coast", "sea", "wave", "boat", "pier", "harbor", "shore", "sandbar", "drought", "mud", "ruin", "wreck", "debris"]

# Helpers: text cleaning and keyword extraction
def clean_text(t: str):
    t = re.sub(r"http\S+", " ", t)          # remove urls
    t = re.sub(r"[^A-Za-z0-9\s]", " ", t)  # remove punctuation
    t = re.sub(r"\s+", " ", t).strip()
    return t.lower()

def extract_keywords_from_texts(texts, top_n=15):
    all_words = []
    for t in texts:
        for w in clean_text(t).split():
            if w not in STOPWORDS and len(w) > 2:
                all_words.append(w)
    return [w for w, _ in Counter(all_words).most_common(top_n)]

# Hazard scoring from text
def calculate_text_hazard_score(text):
    text_l = clean_text(text)
    score = 0
    # match whole words with regex
    for kw, weight in HAZARD_WEIGHTS.items():
        matches = len(re.findall(r"\b{}\b".format(re.escape(kw)), text_l))
        score += matches * weight
    # urgency heuristics
    urgency = text.count("!") + sum(1 for w in text.split() if w.isupper() and len(w) > 1)
    score += min(urgency * 1.5, 4)  # small cap for punctuation/caps
    return float(score)

# Classify hazard risk from numeric score using thresholds
def risk_from_score(score):
    # These thresholds can be tuned
    if score >= 6:
        return "High"
    elif score >= 3:
        return "Medium"
    else:
        return "Low"

# Image hazard scoring using image classifier labels
def calculate_image_hazard_score(pil_image):
    """
    Uses image classification pipeline labels; if labels contain hazard keywords,
    increase score by label confidence scaled to [0..5].
    """
    try:
        results = image_pipeline(pil_image, top_k=5)
    except Exception as e:
        # if the image pipeline fails for some reason, return 0
        return 0.0, []
    score = 0.0
    matched_labels = []
    for r in results:
        label = r.get("label", "").lower()
        conf = float(r.get("score", 0.0))
        # check if any IMAGE_HAZARD_KEYWORDS appear in label text
        for key in IMAGE_HAZARD_KEYWORDS:
            if key in label:
                # scale confidence to 0..5
                score += conf * 5.0
                matched_labels.append((label, conf))
                break
    # cap to a sensible maximum
    score = min(score, 5.0)
    return float(round(score, 3)), matched_labels

# Combine text & image scores into final score & interpretation
def fuse_scores(text_score, image_score, image_confident=False):
    """
    - Normalize text_score roughly: expect max meaningful text_score maybe around 10.
    - text_norm = text_score / 10 (cap 1.0)
    - image_norm = image_score / 5 (cap 1.0)
    - default weights: text 0.6, image 0.4
    - if image_confident (image_score high), boost image weight
    """
    text_norm = min(text_score / 10.0, 1.0)
    image_norm = min(image_score / 5.0, 1.0)
    if image_confident and image_score >= 3.5:
        w_image = 0.6
        w_text = 0.4
    else:
        w_image = 0.4
        w_text = 0.6
    fused = w_text * text_norm + w_image * image_norm
    # scale to 0..10 for readability
    fused_scaled = fused * 10
    return float(round(fused_scaled, 3)), {"text_norm": text_norm, "image_norm": image_norm, "w_text": w_text, "w_image": w_image}

# Fetch recent tweets with media (attempt)
def fetch_tweets_with_media(keywords, max_results=20):
    """
    Builds v2 query with OR between keywords. Requests expansions for media.
    Returns list of dicts: {'text':..., 'media_urls': [..]}
    """
    if not twitter_client:
        return []
    query = "(" + " OR ".join(keywords) + ") -is:retweet lang:en"
    # request expansions for media and media fields (url)
    try:
        resp = twitter_client.search_recent_tweets(query=query, max_results=max_results,
                                                  expansions=['attachments.media_keys'],
                                                  media_fields=['url','preview_image_url','type'])
    except Exception as e:
        st.warning(f"Twitter API error: {e}")
        return []
    tweets = []
    includes = resp.includes or {}
    media_map = {}
    # build media map if present
    if 'media' in includes:
        for m in includes['media']:
            # m.media_key and m.url (if image) may exist
            key = getattr(m, 'media_key', None)
            url = getattr(m, 'url', None) or getattr(m, 'preview_image_url', None)
            if key and url:
                media_map[key] = url
    # iterate data
    if resp.data:
        for t in resp.data:
            text = t.text
            m_urls = []
            if hasattr(t, 'attachments') and getattr(t.attachments, 'media_keys', None):
                for mk in t.attachments.media_keys:
                    if mk in media_map:
                        m_urls.append(media_map[mk])
            tweets.append({'text': text, 'media_urls': m_urls})
    return tweets

# Utility to download image from URL to PIL
def download_image_from_url(url):
    try:
        r = requests.get(url, timeout=8)
        img = Image.open(io.BytesIO(r.content)).convert("RGB")
        return img
    except Exception:
        return None

# Mock data for offline/hackathon demo
MOCK_TWEETS = [
    {"text": "Huge tsunami warning issued for coastal areas!", "media_urls": []},
    {"text": "Massive storm surge expected tonight, stay safe!", "media_urls": []},
    {"text": "Cyclone approaching, authorities on high alert!", "media_urls": []},
    {"text": "Flood waters rising fast, avoid low-lying areas!", "media_urls": []},
    {"text": "High waves reported along the coast, surfing dangerous!", "media_urls": []}
]
# Optionally provide a sample mock image (you can place a sample.jpg next to the file)
MOCK_IMAGE_PATH = None  # set to "sample.jpg" if you want an image fallback

# Streamlit UI
st.set_page_config(page_title="Multimodal Ocean Hazard Analyzer", layout="wide")
st.title("🌊 Multimodal Ocean Hazard Analyzer — Text + Image + Social Media")
st.markdown("""
This demo combines **text analysis**, **image analysis**, and **Twitter** (optional) to detect ocean hazards.
- Provide text and optional image, or fetch recent tweets for keywords.
- Uses weighted keyword scoring + transformers sentiment + image classification to fuse a final hazard level.
""")

# Sidebar options
st.sidebar.header("Mode & Settings")
mode = st.sidebar.radio("Mode", ["Custom Input", "Twitter Keywords (live)", "Batch Mock Demo"])
keywords_input = st.sidebar.text_input("Keywords (space-separated)", "tsunami storm surge flood cyclone")
keywords = [k.strip() for k in keywords_input.split() if k.strip()]
tweet_count = st.sidebar.slider("Max tweets to fetch", 1, 50, 10)
use_image_model = st.sidebar.checkbox("Enable image analysis", value=True)
show_debug = st.sidebar.checkbox("Show debug details (scores / matched labels)", value=False)

# Content area columns
col_l, col_r = st.columns([2, 1])

with col_l:
    if mode == "Custom Input":
        st.subheader("Custom Text + Image")
        user_text = st.text_area("Enter text (tweet / report)", height=150)
        uploaded_file = st.file_uploader("Upload an image (optional)", type=["jpg", "jpeg", "png"])
        run_btn = st.button("Analyze Input")
        if run_btn:
            if not user_text and not uploaded_file:
                st.warning("Please provide text and/or an image for analysis.")
            else:
                # text analysis
                t_score = calculate_text_hazard_score(user_text) if user_text else 0.0
                sentiment_result = sentiment_pipeline(user_text) if user_text else [{'label': 'NEUTRAL', 'score': 1.0}]
                sent_label = sentiment_result[0]['label']
                z = zero_shot_pipeline(user_text, candidate_labels=["hazard alert", "safe", "neutral"]) if user_text else {'labels': ['neutral']}
                text_hazard_class = z['labels'][0]

                # image analysis
                image_score = 0.0
                matched_image_labels = []
                if uploaded_file and use_image_model:
                    pil = Image.open(uploaded_file).convert("RGB")
                    image_score, matched_image_labels = calculate_image_hazard_score(pil)

                elif uploaded_file is None and MOCK_IMAGE_PATH:
                    pil = Image.open(MOCK_IMAGE_PATH).convert("RGB")
                    image_score, matched_image_labels = calculate_image_hazard_score(pil)

                # fuse
                image_confident = image_score >= 3.0
                fused_score, norms = fuse_scores(t_score, image_score, image_confident=image_confident)
                final_risk = risk_from_score(fused_score / 1.0)  # risk_from_score expects 0..10 style
                st.markdown("### Result")
                st.write(f"**Text Hazard Score:** {t_score:.2f}")
                st.write(f"**Text Hazard Class (zero-shot):** {text_hazard_class}")
                st.write(f"**Text Sentiment:** {sent_label}")
                st.write(f"**Image Hazard Score:** {image_score:.2f}")
                if matched_image_labels:
                    st.write("**Matched image labels:**")
                    for lbl, conf in matched_image_labels:
                        st.write(f"- {lbl} ({conf:.2f})")
                st.write(f"**Fused Score (0-10):** {fused_score:.2f}")
                st.markdown(f"## 🔴 Final Hazard Level: **{final_risk}**")

                if show_debug:
                    st.write("Debug:", norms)

    elif mode == "Twitter Keywords (live)":
        st.subheader("Fetch Tweets for Keywords & Analyze (live)")
        st.write("If Twitter credentials are not configured, toggle to 'Batch Mock Demo' or add BEARER token in `.env`.")
        if not twitter_client:
            st.warning("Twitter client not configured or failed. Add TWITTER_BEARER_TOKEN to `.env` to enable live fetch.")
        run_twitter = st.button("Fetch & Analyze Tweets")
        if run_twitter:
            if not keywords:
                st.warning("Enter at least one keyword.")
            else:
                tweets_data = fetch_tweets_with_media(keywords, max_results=tweet_count) if twitter_client else MOCK_TWEETS
                if not tweets_data:
                    st.info("No tweets found. Using mock data.")
                    tweets_data = MOCK_TWEETS
                # aggregate results list
                rows = []
                for tw in tweets_data:
                    text = tw.get("text") if isinstance(tw, dict) else tw
                    media_urls = tw.get("media_urls", []) if isinstance(tw, dict) else []
                    # text metrics
                    t_score = calculate_text_hazard_score(text)
                    sent_label = sentiment_pipeline(text)[0]['label'] if text else "NEUTRAL"
                    z = zero_shot_pipeline(text, candidate_labels=["hazard alert", "safe", "neutral"]) if text else {'labels': ['neutral']}
                    text_hazard_class = z['labels'][0]
                    # images (if any)
                    image_score = 0.0
                    matched_labels = []
                    for url in media_urls:
                        img = download_image_from_url(url)
                        if img:
                            iscore, mlabels = calculate_image_hazard_score(img)
                            # keep the max image score across attachments
                            if iscore > image_score:
                                image_score = iscore
                                matched_labels = mlabels
                    # fuse
                    image_confident = image_score >= 3.0
                    fused_score, norms = fuse_scores(t_score, image_score, image_confident=image_confident)
                    final_risk = risk_from_score(fused_score)
                    rows.append({
                        "text": text,
                        "media_count": len(media_urls),
                        "text_score": round(t_score, 2),
                        "image_score": round(image_score, 2),
                        "fused_score": fused_score,
                        "final_risk": final_risk,
                        "sentiment": sent_label,
                        "text_hazard_class": text_hazard_class,
                        "matched_image_labels": matched_labels
                    })

                df = pd.DataFrame(rows)
                st.subheader("Analyzed Tweets")
                st.dataframe(df[["final_risk", "fused_score", "text_score", "image_score", "sentiment", "text_hazard_class", "media_count"]].sort_values(by="fused_score", ascending=False))

                # Visualizations
                if not df.empty:
                    # risk distribution
                    st.subheader("Risk Distribution")
                    fig1, ax1 = plt.subplots()
                    df['final_risk'].value_counts().reindex(["High","Medium","Low"]).fillna(0).plot(kind='bar', ax=ax1, color=['red','orange','green'])
                    ax1.set_ylabel("Count")
                    st.pyplot(fig1)

                    # sentiment pie
                    st.subheader("Sentiment Distribution")
                    fig2, ax2 = plt.subplots()
                    df['sentiment'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax2)
                    ax2.set_ylabel("")
                    st.pyplot(fig2)

                    # word cloud
                    st.subheader("Trending Keywords")
                    kw = extract_keywords_from_texts(df['text'].tolist(), top_n=30)
                    if kw:
                        wc = WordCloud(width=800, height=300, background_color='white').generate(" ".join(kw))
                        fig3, ax3 = plt.subplots(figsize=(10,3))
                        ax3.imshow(wc, interpolation='bilinear')
                        ax3.axis('off')
                        st.pyplot(fig3)

    else:  # Batch Mock Demo
        st.subheader("Batch Mock Demo (offline)")
        if st.button("Run Mock Demo"):
            tweets_data = MOCK_TWEETS
            rows = []
            for tw in tweets_data:
                text = tw.get("text") if isinstance(tw, dict) else tw
                t_score = calculate_text_hazard_score(text)
                sent_label = sentiment_pipeline(text)[0]['label']
                z = zero_shot_pipeline(text, candidate_labels=["hazard alert", "safe", "neutral"])
                text_hazard_class = z['labels'][0]
                image_score = 0.0
                fused_score, norms = fuse_scores(t_score, image_score)
                final_risk = risk_from_score(fused_score)
                rows.append({
                    "text": text,
                    "text_score": round(t_score,2),
                    "image_score": image_score,
                    "fused_score": fused_score,
                    "final_risk": final_risk,
                    "sentiment": sent_label,
                    "text_hazard_class": text_hazard_class
                })
            df = pd.DataFrame(rows)
            st.dataframe(df)
            st.subheader("Risk Distribution")
            fig1, ax1 = plt.subplots()
            df['final_risk'].value_counts().reindex(["High","Medium","Low"]).fillna(0).plot(kind='bar', ax=ax1, color=['red','orange','green'])
            st.pyplot(fig1)

# Footer / notes
st.markdown("---")
st.markdown("""
**Notes & Limitations**  
- The image classifier is *general-purpose*; matching labels to hazard keywords is heuristic. For production you'd want a fine-tuned model for floods/tsunami/shoreline damage.  
- Twitter API v2 media access may be limited by your app access level; mock mode ensures demo stability.  
- Thresholds and weights can be tuned with labeled data for better accuracy.
""")
