import sys
import types
import base64

# Create dummy modules to avoid importing heavy deps during testing
audio_utils = types.ModuleType("app.audio_utils")
def extract_features(audio_bytes):
    return [0.1, 0.2, 0.3]
audio_utils.extract_features = extract_features

model_loader = types.ModuleType("app.model_loader")
def predict(features):
    return 0.8
model_loader.predict = predict

sys.modules["app.audio_utils"] = audio_utils
sys.modules["app.model_loader"] = model_loader

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_detect_voice_success():
    payload = {
        "language": "English",
        "audioFormat": "mp3",
        "audioBase64": base64.b64encode(b"validaudio").decode()
    }
    headers = {"X-API-Key": "memesrock123"}
    resp = client.post("/api/voice-detection", json=payload, headers=headers)
    assert resp.status_code == 200
    json = resp.json()
    assert json["status"] == "success"
    assert json["classification"] == "AI_GENERATED"
    assert 0.0 <= json["confidenceScore"] <= 1.0
