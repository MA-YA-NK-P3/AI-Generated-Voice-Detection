from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import base64
import tempfile
import os

from detector import analyze_voice

# ======================
# CONFIG
# ======================
API_KEY = "memesrock123"

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam"
}

SUPPORTED_FORMATS = {"mp3", "wav"}

# ======================
# APP INIT
# ======================
app = FastAPI(
    title="AI Generated Voice Detection API",
    version="1.0.0"
)

# ======================
# REQUEST MODEL
# ======================
class VoiceRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str

# ======================
# HEALTH CHECK
# ======================
@app.get("/health")
def health():
    return {"status": "ok"}

# ======================
# MAIN ENDPOINT
# ======================
@app.post("/api/voice-detection")
def voice_detection(
    req: VoiceRequest,
    x_api_key: str = Header(None, alias="x-api-key")
):
    # 🔐 API KEY CHECK
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # 🌍 LANGUAGE CHECK
    if req.language not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language. Use one of {list(SUPPORTED_LANGUAGES.keys())}"
        )

    # 🎧 AUDIO FORMAT CHECK
    audio_format = req.audioFormat.lower()
    if audio_format not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=400,
            detail="Only mp3 or wav audio formats are supported"
        )

    # 📦 BASE64 CHECK
    if not req.audioBase64:
        raise HTTPException(status_code=400, detail="audioBase64 is required")

    # 🔁 BASE64 DECODE
    try:
        audio_bytes = base64.b64decode(req.audioBase64, validate=True)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Base64 audio data")

    # 🗂️ WRITE TEMP AUDIO FILE
    suffix = f".{audio_format}"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        audio_path = tmp.name

    # 🧠 RUN MODEL
    try:
        classification, confidence, explanation = analyze_voice(audio_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

    # ✅ SUCCESS RESPONSE
    return {
        "status": "success",
        "language": SUPPORTED_LANGUAGES[req.language],
        "classification": classification,
        "confidenceScore": round(float(confidence), 2),
        "explanation": explanation
    }
