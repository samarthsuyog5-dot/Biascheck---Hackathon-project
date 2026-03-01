from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI(title="BiasCheck API", version="1.0")

# Allow frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Request Model
# ----------------------------
class TextInput(BaseModel):
    text: str
    mode: str = "Global Neutral"

# ----------------------------
# Bias Dictionary with Categories
# ----------------------------
BIAS_TERMS = {
    "young": {"replacement": "motivated", "category": "Age Bias"},
    "digital native": {"replacement": "tech-savvy", "category": "Age Bias"},
    "rockstar": {"replacement": "highly skilled professional", "category": "Gender-Coded"},
    "aggressive": {"replacement": "goal-oriented", "category": "Gender-Coded"},
    "dominant": {"replacement": "confident", "category": "Gender-Coded"},
    "competitive": {"replacement": "fast-paced", "category": "Work Culture Bias"},
    "dominate": {"replacement": "lead", "category": "Work Culture Bias"},
}

# ----------------------------
# Detect Bias
# ----------------------------
def detect_bias(text: str):
    detected = []
    fixed_text = text

    for term, info in BIAS_TERMS.items():
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text, re.IGNORECASE):
            detected.append({
                "biased_term": term,
                "category": info["category"],
                "suggestion": info["replacement"]
            })

            fixed_text = re.sub(
                pattern,
                info["replacement"],
                fixed_text,
                flags=re.IGNORECASE
            )

    return detected, fixed_text

# ----------------------------
# Score Calculation
# ----------------------------
def calculate_score(count):
    score = 100 - (count * 12)
    return max(0, score)

# ----------------------------
# API Endpoint
# ----------------------------
@app.post("/analyze")
def analyze(data: TextInput):

    if not data.text.strip():
        return {
            "bias_score": 100,
            "detected_bias": [],
            "auto_fixed_text": "",
            "message": "No text provided."
        }

    detected, fixed = detect_bias(data.text)
    score = calculate_score(len(detected))

    return {
        "bias_score": score,
        "detected_bias": detected,
        "auto_fixed_text": fixed,
        "mode_used": data.mode
    }

@app.get("/")
def root():
    return {"message": "BiasCheck API Running"}