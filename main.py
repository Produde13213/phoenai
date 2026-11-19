from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
AUDIO = ROOT / "ttsfree-marathi-take2.wav"

app = FastAPI(title="PhoenAI", version="0.1.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")

MENU = {
    "1": {"title": "तक्रार निवारण", "message": "तक्रार निवारण विभागाची माहिती मिळवण्यासाठी कृपया कार्यालयीन वेळेत प्रतिनिधीशी संपर्क साधा."},
    "2": {"title": "शाळाविषयक माहिती", "message": "शाळाविषयक माहितीसाठी संबंधित शिक्षण विभागाशी संपर्क साधा."},
    "3": {"title": "शिष्यवृत्ती", "message": "शिष्यवृत्तीविषयक माहितीसाठी संबंधित शासकीय कार्यालयाची अधिकृत माहिती तपासा."},
    "4": {"title": "प्रतिनिधी", "message": "प्रतिनिधीकडे कॉल हस्तांतरित करण्याची सुविधा अद्याप जोडलेली नाही. कृपया नंतर पुन्हा प्रयत्न करा."},
}

class DigitRequest(BaseModel):
    digit: str

@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/health")
def health():
    return {"status": "ok", "service": "PhoenAI", "telephony_connected": False}

@app.get("/api/greeting")
def greeting():
    return {
        "text": "नमस्कार! दिव्यांग कल्याण आयुक्तालयामध्ये आपले स्वागत आहे. तक्रार निवारणासाठी एक दाबा. शाळाविषयक माहितीसाठी दोन दाबा. शिष्यवृत्तीसाठी तीन दाबा. आमच्या प्रतिनिधीशी बोलण्यासाठी चार दाबा.",
        "audio_available": AUDIO.is_file(),
        "audio_url": "/api/greeting/audio" if AUDIO.is_file() else None,
    }

@app.get("/api/greeting/audio")
def greeting_audio():
    if not AUDIO.is_file():
        return {"error": "Greeting audio file not found"}
    return FileResponse(AUDIO, media_type="audio/wav", filename=AUDIO.name)

@app.get("/api/menu")
def menu():
    return MENU

@app.post("/api/ivr/digit")
def select_digit(body: DigitRequest):
    digit = body.digit.strip()
    if digit not in MENU:
        return {"ok": False, "message": "कृपया १ ते ४ पैकी एक पर्याय निवडा."}
    return {"ok": True, "digit": digit, **MENU[digit]}
