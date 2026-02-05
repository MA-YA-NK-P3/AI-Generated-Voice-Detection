from fastapi import FastAPI, Header, Form
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
import base64
import logging

from app.config import API_KEY, SUPPORTED_LANGUAGES
from app.audio_utils import extract_features
from app.model_loader import predict

logger = logging.getLogger("uvicorn.error")
app = FastAPI(title="AI Generated Voice Detection API")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/docs#/default/detect_voice_api_voice_detection_post")

class VoiceRequest(BaseModel):
    language: str
    audioFormat: str
    audioBase64: str


def _process_voice(language: str, audioFormat: str, audioBase64: str, x_api_key: str):
    # Log incoming request for debugging
    try:
        logger.info("Incoming voice-detection request: header X-API-Key=%s, body=%s", x_api_key, {"language": language, "audioFormat": audioFormat})
    except Exception:
        logger.info("Incoming voice-detection request: header X-API-Key present=%s", bool(x_api_key))

    # API key validation
    if not x_api_key or x_api_key != API_KEY:
        logger.warning("Invalid or missing API key: %s", x_api_key)
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "message": "Invalid or missing API key"
            }
        )

    # Language validation (case-insensitive)
    language_norm = language.strip().title() if language else ""
    if language_norm not in SUPPORTED_LANGUAGES:
        logger.warning("Unsupported language received: %s", language)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": f"Unsupported language. Supported languages: {', '.join(SUPPORTED_LANGUAGES)}"
            }
        )

    # Audio format validation
    if not audioFormat or audioFormat.lower() != "mp3":
        logger.warning("Unsupported audio format received: %s", audioFormat)
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Unsupported audio format. Only 'mp3' is accepted."
            }
        )

    if not audioBase64:
        logger.warning("Missing audioBase64 data in request")
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Missing audioBase64 data."
            }
        )

    try:
        # validate base64; raises binascii.Error for invalid input
        audio_bytes = base64.b64decode(audioBase64, validate=True)
    except Exception as e:
        logger.warning("Invalid base64 audio data: %s", str(e))
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Invalid base64 audio data."
            }
        )

    try:
        features = extract_features(audio_bytes)
        score = predict(features)

        classification = "AI_GENERATED" if score >= 0.5 else "HUMAN"

        explanation = (
            "Unnatural pitch consistency and robotic speech patterns detected"
            if classification == "AI_GENERATED"
            else "Natural pitch variation and human speech characteristics detected"
        )

        return {
            "status": "success",
            "language": language_norm,
            "classification": classification,
            "confidenceScore": round(score, 2),
            "explanation": explanation
        }

    except Exception as e:
        logger.exception("Error processing audio: %s", str(e))
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error processing audio"
            }
        )


@app.post("/api/voice-detection")
def detect_voice(
    request: VoiceRequest,
    x_api_key: str = Header(None, alias="X-API-Key")
):
    return _process_voice(request.language, request.audioFormat, request.audioBase64, x_api_key)


@app.post("/api/voice-detection/form")
def detect_voice_form(
    language: str = Form(...),
    audioFormat: str = Form(...),
    audioBase64: str = Form(...),
    x_api_key: str = Header(None, alias="X-API-Key")
):
    """Accept multipart/form-data (e.g., Postman form-data) to support clients that aren't sending JSON."""
    return _process_voice(language, audioFormat, audioBase64, x_api_key)

    try:
        features = extract_features(audio_bytes)
        score = predict(features)

        classification = "AI_GENERATED" if score >= 0.5 else "HUMAN"

        explanation = (
            "Unnatural pitch consistency and robotic speech patterns detected"
            if classification == "AI_GENERATED"
            else "Natural pitch variation and human speech characteristics detected"
        )

        return {
            "status": "success",
            "language": language,
            "classification": classification,
            "confidenceScore": round(score, 2),
            "explanation": explanation
        }

    except Exception as e:
        # Log exception in real app; return 500 to indicate server-side error
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error processing audio"
            }
        )
