from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from app_multimodal_hazard import (
    calculate_text_hazard_score,
    calculate_image_hazard_score,
    fuse_scores,
    risk_from_score,
    sentiment_pipeline,
    zero_shot_pipeline,
    download_image_from_url,
)
from PIL import Image
import io

app = FastAPI(title="Multimodal Hazard Analyzer API")


class TextRequest(BaseModel):
    text: str

class FuseRequest(BaseModel):
    text_score: float
    image_score: float



@app.post("/analyze-text")
def analyze_text(req: TextRequest):
    """Analyze hazard from text only"""
    t_score = calculate_text_hazard_score(req.text)
    sentiment = sentiment_pipeline(req.text)[0]
    zero = zero_shot_pipeline(req.text, candidate_labels=["hazard alert", "safe", "neutral"])
    return {
        "text": req.text,
        "text_score": t_score,
        "sentiment": sentiment,
        "zero_shot": zero,
        "risk": risk_from_score(t_score),
    }

@app.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...)):
    """Analyze hazard from an uploaded image"""
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    score, labels = calculate_image_hazard_score(image)
    return {
        "image_score": score,
        "matched_labels": labels,
        "risk": risk_from_score(score),
    }

@app.post("/analyze-fuse")
def analyze_fuse(req: FuseRequest):
    """Fuse text + image hazard scores"""
    fused, norms = fuse_scores(req.text_score, req.image_score)
    return {
        "fused_score": fused,
        "norms": norms,
        "risk": risk_from_score(fused),
    }

@app.get("/")
def root():
    return {"message": "🌊 Multimodal Hazard Analyzer API is running!"}
