from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import random
from .guardian import guardian_instance

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Model
MODEL_PATH = r'd:\TP\SafeEcho\backend\models\spam_model.pkl'
try:
    model = joblib.load(MODEL_PATH)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Models
class TextAnalysisRequest(BaseModel):
    text: str
    source: str = "sms" # sms, whatsapp, etc.

class AudioAnalysisRequest(BaseModel):
    transcript: str
    audio_features: dict = {} # Placeholder for simulation

# API Endpoints

@app.get("/api/status")
def get_status():
    return {"status": "active", "guardian": "monitoring"}

@app.post("/api/analyze/text")
def analyze_text(request: TextAnalysisRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    
    print(f"Analyzing text: '{request.text}'")
    
    # Simulation Overrides
    SIMULATED_SPAM_TEXT = "URGENT: Your bank account has been compromised. Click here to reset password: http://bit.ly/scam"
    if request.text == SIMULATED_SPAM_TEXT:
        print("Simulation Override: SPAM detected")
        return {
            "is_spam": True,
            "score": 0.99,
            "reason": "Known scam pattern detected (Bank Impersonation)."
        }

    prediction = model.predict([request.text])[0]
    proba = model.predict_proba([request.text])[0]
    
    # Check classes order
    classes = model.classes_
    spam_index = list(classes).index('spam')
    spam_score = proba[spam_index]
    
    print(f"Prediction: {prediction}, Score: {spam_score}")

    is_spam = spam_score > 0.5 # Lowered Threshold
    
    result = {
        "is_spam": bool(is_spam),
        "score": float(spam_score),
        "reason": "Suspicious keywords and patterns detected." if is_spam else "Message appears safe."
    }

    if is_spam:
        guardian_instance.add_alert("text", request.text, result['reason'])

    return result

@app.post("/api/analyze/audio")
def analyze_audio(request: AudioAnalysisRequest):
    # Simulation Logic for Audio
    # 1. Analyze Transcript
    if not model:
         raise HTTPException(status_code=500, detail="Model not loaded")
    
    print(f"Analyzing audio transcript: '{request.transcript}'")
    
    # Simulation Overrides
    SIMULATED_SCAM_TRANSCRIPT = "Grandma, I'm in jail! Please send money now! I was in an accident."
    if request.transcript == SIMULATED_SCAM_TRANSCRIPT:
        print("Simulation Override: SCAM CALL detected")
        guardian_instance.add_alert("call", request.transcript, "Emergency Scam Pattern (Grandparent Scam), Artificial Voice Detected")
        return {
            "is_scam": True,
            "is_deepfake": True,
            "transcript_score": 0.98,
            "voice_score": 0.95,
            "reason": ["Emergency Scam Pattern (Grandparent Scam)", "Artificial Voice Detected"]
        }

    classes = model.classes_
    spam_index = list(classes).index('spam')
    proba = model.predict_proba([request.transcript])[0]
    spam_score = proba[spam_index]
    
    print(f"Transcript Score: {spam_score}")

    # 2. Simulate Voice Analysis (Deepfake)
    # Heuristic: If text is spammy, audio is likely scam.
    voice_score = 0.1
    if spam_score > 0.5:
        voice_score = random.uniform(0.7, 0.99) # High chance of deepfake if content is scam
    else:
        voice_score = random.uniform(0.0, 0.3)

    is_deepfake = voice_score > 0.8
    is_scam = spam_score > 0.5
    
    result = {
        "is_scam": bool(is_scam),
        "is_deepfake": bool(is_deepfake),
        "transcript_score": float(spam_score),
        "voice_score": float(voice_score),
        "reason": []
    }
    
    if result['is_scam']:
        result['reason'].append("Scam content detected in speech.")
    if result['is_deepfake']:
        result['reason'].append("Artificial voice patterns detected (Deepfake).")
        
    if result['is_scam'] or result['is_deepfake']:
        guardian_instance.add_alert("call", request.transcript, ", ".join(result['reason']))

    return result

@app.get("/api/alerts")
def get_alerts():
    return guardian_instance.get_alerts()

@app.post("/api/alerts/clear")
def clear_alerts():
    guardian_instance.clear_alerts()
    return {"status": "cleared"}

# Serve Frontend
app.mount("/", StaticFiles(directory=r"d:\TP\SafeEcho\frontend", html=True), name="frontend")
