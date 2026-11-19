import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Literal

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"

# Load .env if present. Windows OS environment variables are also supported.
load_dotenv(ROOT / ".env")

NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"
MODEL = os.getenv("NVIDIA_MODEL", DEFAULT_MODEL)
API_KEY = os.getenv("NVIDIA_API_KEY", "").strip()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "").strip()

app = FastAPI(
    title="PhoenAI",
    description="Marathi-language information assistant prototype",
    version="0.5.0",
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

MENU = {
    "1": {
        "title": "तक्रार निवारण",
        "message": "तक्रार पाठवण्यासाठी पहिला पर्याय निवडा. डेमोमध्ये कृपया वैयक्तिक किंवा संवेदनशील माहिती लिहू नका.",
        "choices": {
            "1": {"label": "नवीन तक्रार पाठवा", "message": "खालील फॉर्ममध्ये तक्रारीचा प्रकार आणि थोडक्यात वर्णन भरा. कृपया नाव, फोन, पत्ता, Aadhaar, वैद्यकीय किंवा इतर वैयक्तिक माहिती लिहू नका."},
            "2": {"label": "तक्रारीची स्थिती", "message": "या डेमोला कार्यालयाच्या तक्रार नोंदणी प्रणालीशी जोडलेले नाही, त्यामुळे तक्रारीची स्थिती तपासता येत नाही. अधिकृत स्थितीसाठी संबंधित कार्यालयाशी संपर्क साधा."},
        },
    },
    "2": {
        "title": "शाळाविषयक माहिती",
        "message": "शाळांबाबत कोणती माहिती हवी आहे?",
        "choices": {
            "1": {"label": "प्रवेशाबाबत", "message": "प्रवेशाची पात्रता, कागदपत्रे आणि तारखा शाळा व लागू सरकारी नियमांनुसार बदलू शकतात. संबंधित शाळा किंवा शिक्षण विभागाकडून अद्ययावत अधिकृत माहिती घ्या."},
            "2": {"label": "सुविधा व सहाय्य", "message": "शाळेत उपलब्ध प्रवेशयोग्यता सुविधा आणि विद्यार्थ्यांसाठी सहाय्य यांची माहिती थेट संबंधित शाळेकडून लेखी स्वरूपात मागा. या डेमोमध्ये कोणत्याही विशिष्ट शाळेच्या सुविधांची पडताळणी केलेली नाही."},
            "3": {"label": "शाळेविषयी तक्रार", "message": "अडचणीचे संक्षिप्त वर्णन, संबंधित शाळेचे नाव आणि घटना घडल्याची तारीख तयार ठेवा. अधिकृत तक्रार कुठे नोंदवायची हे शिक्षण विभागाकडून तपासा. हा डेमो तक्रार दाखल करत नाही."},
        },
    },
    "3": {
        "title": "शिष्यवृत्ती",
        "message": "शिष्यवृत्तीबाबत कोणती मदत हवी आहे?",
        "choices": {
            "1": {"label": "पात्रता", "message": "शिष्यवृत्तीची पात्रता योजनेनुसार बदलते. अधिकृत योजनेचे नाव आणि चालू वर्षाची शासन सूचना तपासल्याशिवाय पात्रता निश्चित सांगता येणार नाही."},
            "2": {"label": "अर्ज प्रक्रिया", "message": "अर्ज करण्यापूर्वी योजनेची अधिकृत सूचना, अर्जाची पद्धत, आवश्यक कागदपत्रे आणि अंतिम तारीख तपासा. या डेमोमध्ये कोणतीही अर्ज सेवा जोडलेली नाही."},
            "3": {"label": "अर्जाची स्थिती", "message": "या डेमोला शासकीय शिष्यवृत्ती पोर्टलशी जोडलेले नाही, त्यामुळे अर्जाची स्थिती तपासता येत नाही. अधिकृत पोर्टल किंवा संबंधित विभागाकडे चौकशी करा."},
        },
    },
    "4": {
        "title": "प्रतिनिधी",
        "message": "प्रतिनिधीशी बोलण्याची विनंती नोंदवण्याचा पर्याय या डेमोमध्ये उपलब्ध नाही. प्रत्यक्ष फोन हस्तांतरण होत नाही. कार्यालयाचा अधिकृत संपर्क क्रमांक जोडलेला नसल्यामुळे तो येथे दाखवलेला नाही.",
        "choices": {},
    },
}


EN_MENU = {
    "1": {"title": "Complaint support", "message": "Choose an option for complaint support. Do not enter personal or sensitive information in this demo.", "choices": {
        "1": {"label": "Submit a demo complaint", "message": "Use the form below to describe the issue briefly. Do not include names, phone numbers, addresses, Aadhaar, medical details, or other personal information."},
        "2": {"label": "Check complaint status", "message": "This demo is not connected to the office complaint system, so it cannot check a complaint status. Contact the relevant office for an official update."}}},
    "2": {"title": "School information", "message": "What school-related information do you need?", "choices": {
        "1": {"label": "Admissions", "message": "Admission eligibility, documents and dates vary by school and applicable rules. Check current official information with the school or education department."},
        "2": {"label": "Facilities and support", "message": "Ask the school directly for written details about accessibility facilities and student support. This demo has not verified facilities at any specific school."},
        "3": {"label": "School-related complaint", "message": "Keep a brief description, school name and incident date ready. Check with the education department where to file an official complaint. This demo does not file one."}}},
    "3": {"title": "Scholarships", "message": "What scholarship help do you need?", "choices": {
        "1": {"label": "Eligibility", "message": "Eligibility varies by scheme. It cannot be confirmed without checking the official scheme name and current-year government notice."},
        "2": {"label": "Application process", "message": "Before applying, check the official notice, application method, required documents and deadline. No application service is connected to this demo."},
        "3": {"label": "Application status", "message": "This demo is not connected to a government scholarship portal and cannot check application status. Contact the official portal or department."}}},
    "4": {"title": "Speak to a representative", "message": "A request to speak to a representative is not available in this demo. No live phone transfer takes place. An official office contact number has not been connected.", "choices": {}}
}

# Filenames intentionally match the files currently committed to GitHub.
# Option 1 has no dedicated recording yet; never substitute synthetic speech.
AUDIO_FILES = {
    "greeting": "ttsfree-marathi-take2.wav",
    "option_2": "SCHOOLINFO.wav",
    "option_3": "schoolarship.wav",
    "option_4": "talktorep.wav",
    "invalid": "inavlid.wav",
    "idle": "idle.wav",
    "main_menu": "mainmenu.wav",
    "goodbye": "bye.wav",
    "language_english": "choiceeng.wav",
    "language_hindi": "hinchoice.wav",
    "english_greeting": "helloeng.wav",
    "english_option_1": "complaineng.wav",
    "english_option_2": "schoolinfoeng.wav",
    "english_option_3": "scholershipeng.wav",
    "english_option_4": "spekrep.wav",
    "english_invalid": None,
    "english_idle": "idleeng.wav",
    "english_main_menu": "menueng.wav",
    "english_goodbye": "byeeng.wav",
}
DIGIT_AUDIO = {"2": "option_2", "3": "option_3", "4": "option_4"}

BASE_SYSTEM_PROMPT = """You are PhoenAI, a polite Marathi-first information assistant prototype for an office serving persons with disabilities in Maharashtra.
Reply in clear, simple Marathi by default. If the user writes in English, you may reply in English.
Be respectful, concise, and accessible.
Only state office procedures, addresses, phone numbers, deadlines, eligibility rules, or government benefits when those facts are explicitly provided in the conversation. Never invent official information, promise an application outcome, claim to have filed a complaint, or claim to transfer a phone call.
If you do not know an official fact, say that you do not have verified information and recommend checking with the relevant office.
Do not ask callers to share Aadhaar numbers, passwords, OTPs, bank details, medical records, or other sensitive personal information.
This is a prototype, not an official government service. Do not claim otherwise."""

PROMPT_FILE = ROOT / "sysprompt.txt"


def load_system_prompt() -> str:
    """Load editable operator instructions while retaining mandatory safety rules."""
    custom = ""
    try:
        custom = PROMPT_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        pass
    if not custom:
        return BASE_SYSTEM_PROMPT
    return BASE_SYSTEM_PROMPT + "\n\nAdditional operator instructions (editable sysprompt.txt):\n" + custom


SYSTEM_PROMPT = load_system_prompt()


class DigitRequest(BaseModel):
    digit: str = Field(min_length=1, max_length=2)
    sub_option: str | None = Field(default=None, max_length=2)
    language: Literal["mr", "en"] = "mr"


class ComplaintRequest(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    description: str = Field(min_length=10, max_length=1500)
    privacy_confirmed: bool


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    history: list[ChatMessage] = Field(default_factory=list, max_length=8)


def audio_path(event: str) -> Path:
    filename = AUDIO_FILES.get(event)
    if not filename:
        raise HTTPException(status_code=404, detail="Unknown audio event")
    path = ROOT / filename
    if not path.is_file():
        raise HTTPException(status_code=404, detail=f"Recording is not available for: {event}")
    return path


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "PhoenAI",
        "version": app.version,
        "ai_configured": bool(API_KEY),
        "model": MODEL,
        "telephony_connected": False,
        "synthetic_speech_enabled": False,
    }


@app.get("/api/config")
def config():
    return {
        "service": "PhoenAI",
        "model": MODEL,
        "ai_configured": bool(API_KEY),
        "telephony_connected": False,
        "synthetic_speech_enabled": False,
    }


@app.get("/api/greeting")
def greeting():
    available = (ROOT / AUDIO_FILES["greeting"]).is_file()
    return {
        "text": (
            "नमस्कार! दिव्यांग कल्याण आयुक्तालयामध्ये आपले स्वागत आहे. "
            "तक्रार निवारणासाठी एक दाबा. शाळाविषयक माहितीसाठी दोन दाबा. "
            "शिष्यवृत्तीसाठी तीन दाबा. प्रतिनिधीशी बोलण्यासाठी चार दाबा."
        ),
        "audio_available": available,
        "audio_url": "/api/audio/greeting" if available else None,
    }


@app.get("/api/audio/{event}")
def get_audio(event: str):
    path = audio_path(event)
    return FileResponse(path, media_type="audio/wav", filename=path.name)


@app.get("/api/audio")
def audio_catalog():
    return {
        event: {
            "available": (ROOT / filename).is_file(),
            "url": f"/api/audio/{event}" if (ROOT / filename).is_file() else None,
            "filename": filename,
        }
        for event, filename in AUDIO_FILES.items()
    }


@app.get("/api/menu")
def menu():
    return MENU



@app.get("/api/demo-check")
def demo_check():
    """Report demo readiness without exposing credentials or personal data."""
    recordings = {
        event: (ROOT / filename).is_file()
        for event, filename in AUDIO_FILES.items()
    }
    required_events = ("greeting", "option_2", "option_3", "option_4", "invalid", "idle", "main_menu", "goodbye")
    return {
        "service": "PhoenAI",
        "ready_for_browser_demo": all(recordings[event] for event in required_events),
        "ai_configured": bool(API_KEY),
        "complaint_webhook_configured": bool(DISCORD_WEBHOOK_URL),
        "recordings": recordings,
        "missing_recordings": [event for event, available in recordings.items() if not available],
        "option_1_recording_required": False,
        "telephony_connected": False,
        "synthetic_speech_enabled": False,
    }


@app.post("/api/ivr/digit")
def select_digit(body: DigitRequest):
    digit = body.digit.strip()

    # 0 always returns to the welcome/main menu.
    if digit == "0" and body.sub_option is None:
        main_event = audio_prefix + "main_menu"
        main_file = AUDIO_FILES.get(main_event) or AUDIO_FILES["main_menu"]
        available = (ROOT / main_file).is_file()
        return {
            "ok": True,
            "digit": "0",
            "title": "Main menu" if body.language == "en" else "मुख्य मेनू",
            "message": ("Welcome to the Office of the Commissioner for Persons with Disabilities. Press 1 for complaint support, 2 for school information, 3 for scholarships, or 4 to request a representative." if body.language == "en" else "नमस्कार! दिव्यांग कल्याण आयुक्तालयामध्ये आपले स्वागत आहे. तक्रार निवारणासाठी एक दाबा. शाळाविषयक माहितीसाठी दोन दाबा. शिष्यवृत्तीसाठी तीन दाबा. प्रतिनिधीशी बोलण्यासाठी चार दाबा."),
            "choices": [{"digit": key, "label": value["title"]} for key, value in active_menu.items()],
            "audio_url": f"/api/audio/{main_event}" if available else None,
            "audio_available": available,
        }

    if digit not in active_menu:
        invalid_event = audio_prefix + "invalid"
        invalid_file = AUDIO_FILES.get(invalid_event)
        return {"ok": False, "message": "Please choose an option from 1 to 4." if body.language == "en" else "कृपया १ ते ४ पैकी एक पर्याय निवडा.", "choices": [], "audio_url": f"/api/audio/{invalid_event}" if invalid_file and (ROOT / invalid_file).is_file() else ("/api/audio/invalid" if body.language == "mr" and (ROOT / AUDIO_FILES["invalid"]).is_file() else None)}

    selected = active_menu[digit]
    if body.sub_option is not None:
        sub_option = body.sub_option.strip()
        choice = selected["choices"].get(sub_option)
        if choice is None:
            return {"ok": False, "message": "Please choose one of the listed options." if body.language == "en" else "कृपया दिलेल्या पर्यायांपैकी एक निवडा.", "choices": [], "audio_url": None}
        return {
            "ok": True,
            "digit": digit,
            "sub_option": sub_option,
            "title": choice["label"],
            "message": choice["message"],
            "choices": [],
            "audio_url": None,
            "audio_available": False,
        }

    audio_event = (f"english_option_{digit}" if body.language == "en" else DIGIT_AUDIO.get(digit))
    audio_file = AUDIO_FILES.get(audio_event) if audio_event else None
    audio_url = f"/api/audio/{audio_event}" if audio_file and (ROOT / audio_file).is_file() else None
    return {
        "ok": True,
        "digit": digit,
        "title": selected["title"],
        "message": selected["message"],
        "choices": [{"digit": key, **value} for key, value in selected["choices"].items()],
        "audio_url": audio_url,
        "audio_available": audio_url is not None,
    }


@app.post("/api/complaints")
def submit_complaint(body: ComplaintRequest):
    """Send a minimal demo complaint to the operator-configured Discord webhook."""
    if not DISCORD_WEBHOOK_URL:
        raise HTTPException(status_code=503, detail="Complaint inbox is not configured on this server.")
    if not body.privacy_confirmed:
        raise HTTPException(status_code=400, detail="Please confirm that you have not included personal or sensitive information.")

    # Only the category and user-written description are sent. Never attach identity/contact data.
    payload = {
        "content": "New PhoenAI demo complaint",
        "embeds": [{
            "title": "Demo complaint received",
            "color": 5793266,
            "fields": [
                {"name": "Category", "value": body.category.strip()[:80], "inline": True},
                {"name": "Description", "value": body.description.strip()[:1500], "inline": False},
            ],
            "footer": {"text": "PhoenAI browser prototype — not an official complaint registration"},
        }],
        "allowed_mentions": {"parse": []},
    }
    request = Request(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "PhoenAI-Demo/0.5"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=8) as response:
            if response.status not in (200, 204):
                raise HTTPException(status_code=502, detail="The complaint inbox did not accept the demo submission.")
    except HTTPError as exc:
        print(f"Discord webhook rejected complaint: HTTP {exc.code}")
        raise HTTPException(status_code=502, detail="The complaint inbox rejected the demo submission.") from exc
    except (URLError, TimeoutError, OSError) as exc:
        print(f"Discord webhook request failed: {type(exc).__name__}")
        raise HTTPException(status_code=502, detail="Could not reach the complaint inbox. Please try again.") from exc

    return {
        "ok": True,
        "message": "तुमची डेमो तक्रार प्राप्त झाली आहे. धन्यवाद!",
        "return_to_main_menu": True,
    }


@app.post("/api/chat")
def chat(body: ChatRequest):
    if not API_KEY:
        raise HTTPException(
            status_code=503,
            detail="NVIDIA_API_KEY is not configured on the server.",
        )

    messages = [{"role": "system", "content": load_system_prompt()}]
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
        return {"reply": answer, "model": MODEL, "audio_url": None}
    except HTTPException:
        raise
    except Exception as exc:
        print(f"NVIDIA API request failed: {type(exc).__name__}")
        raise HTTPException(
            status_code=502,
            detail="The NVIDIA AI request failed. Check the server terminal and API key.",
        ) from exc
