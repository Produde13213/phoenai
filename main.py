import os
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
AUDIO = ROOT / "ttsfree-marathi-take2.wav"

# Load a local .env when present; OS environment variables remain supported.
load_dotenv(ROOT / ".env")

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"
MODEL = os.getenv("NVIDIA_MODEL", DEFAULT_MODEL)
API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()

app = FastAPI(
    title="PhoenAI",
    description="Marathi-language information assistant prototype",
    version="0.2.0",
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

MENU = {
    "1": {
        "title": "तक्रार निवारण",
        "message": "तक्रार निवारणासाठी कृपया आपली तक्रार संबंधित कार्यालयाकडे अधिकृत पद्धतीने नोंदवा. या डेमोमध्ये तक्रार नोंदवली जात नाही.",
    },
    "2": {
        "title": "शाळाविषयक माहिती",
        "message": "शाळाविषयक अचूक माहितीसाठी संबंधित शिक्षण विभागाशी संपर्क साधा. अधिकृत माहिती उपलब्ध नसल्यास आम्ही अंदाज देणार नाही.",
    },
    "3": {
        "title": "शिष्यवृत्ती",
        "message": "शिष्यवृत्तीच्या पात्रता आणि अर्जाच्या माहितीसाठी संबंधित शासकीय विभागाची अधिकृत सूचना तपासा.",
    },
    "4": {
        "title": "प्रतिनिधी",
        "message": "प्रतिनिधीकडे कॉल हस्तांतरित करण्याची सुविधा अद्याप जोडलेली नाही. हा फक्त ब्राउझर डेमो आहे.",
    },
}

SYSTEM_PROMPT = """You are PhoenAI, a polite Marathi-first information assistant prototype for an office serving persons with disabilities in Maharashtra.
Reply in clear, simple Marathi by default. If the user writes in English, you may reply in English.
Be respectful, concise, and accessible.
Only state office procedures, addresses, phone numbers, deadlines, eligibility rules, or government benefits when those facts are explicitly provided in the conversation. Never invent official information, promise an application outcome, claim to have filed a complaint, or claim to transfer a phone call.
If you do not know an official fact, say that you do not have verified information and recommend checking with the relevant office.
Do not ask callers to share Aadhaar numbers, passwords, OTPs, bank details, medical records, or other sensitive personal information.
This is a prototype, not an official government service. Do not claim otherwise."""

class DigitRequest(BaseModel):
    digit: str = Field(min_length=1, max_length=2)

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=8)

@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "PhoenAI",
        "ai_configured": bool(API_KEY),
        "model": MODEL,
        "telephony_connected": False,
    }

@app.get("/api/config")
def config():
    return {
        "service": "PhoenAI",
        "model": MODEL,
        "ai_configured": bool(API_KEY),
        "telephony_connected": False,
    }

@app.get("/api/greeting")
def greeting():
    return {
        "text": (
            "नमस्कार! दिव्यांग कल्याण आयुक्तालयामध्ये आपले स्वागत आहे. "
            "तक्रार निवारणासाठी एक दाबा. शाळाविषयक माहितीसाठी दोन दाबा. "
            "शिष्यवृत्तीसाठी तीन दाबा. प्रतिनिधीशी बोलण्यासाठी चार दाबा."
        ),
        "audio_available": AUDIO.is_file(),
        "audio_url": "/api/greeting/audio" if AUDIO.is_file() else None,
    }

@app.get("/api/greeting/audio")
def greeting_audio():
    if not AUDIO.is_file():
        raise HTTPException(status_code=404, detail="Greeting audio file not found")
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

@app.post("/api/chat")
def chat(body: ChatRequest):
    if not API_KEY:
        raise HTTPException(
            status_code=503,
            detail="NVIDIA_API_KEY is not configured on the server.",
        )

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in body.history[-8:]:
        messages.append({"role": item.role, "content": item.content})
    messages.append({"role": "user", "content": body.message})

    try:
        client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=API_KEY,
            timeout=45.0,
            max_retries=1,
        )
        result = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.6,
            top_p=0.95,
            max_tokens=1400,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        answer = result.choices[0].message.content
        if not answer:
            raise HTTPException(status_code=502, detail="The AI returned an empty response.")
        return {"reply": answer, "model": MODEL}
    except HTTPException:
        raise
    except Exception as exc:
        # Keep credentials and raw provider error details out of browser responses and logs.
        print(f"NVIDIA API request failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="The NVIDIA AI request failed. Check the server terminal and API key.",
        ) from exc
