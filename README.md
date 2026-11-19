# PhoenAI — Marathi Information Assistant

PhoenAI is a Marathi-first browser prototype with an IVR-style menu and an NVIDIA-powered, text-only chat assistant.

## AI model

Default model: `nvidia/nemotron-3.5-super-vl-120b-a12b`

You can override the model with the `NVIDIA_MODEL` environment variable.

## Configure your API key

The application reads `NVIDIA_API_KEY` from the server's operating-system environment. A local `.env` file is also supported. On Windows, environment-variable names are case-insensitive, so an existing `nvidia_api_key` variable is recognized. On Linux they are case-sensitive.

Never paste your key into source code, HTML, GitHub, screenshots, or chat messages.

PowerShell (current terminal only):

```powershell
$env:NVIDIA_API_KEY = "YOUR_NVIDIA_API_KEY"
```

Persistent Windows user variable (run once, then open a new terminal):

```powershell
[Environment]::SetEnvironmentVariable("NVIDIA_API_KEY", "YOUR_NVIDIA_API_KEY", "User")
```

## Run on Windows

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000.

## Prerecorded audio policy

**PhoenAI must not synthesize speech.** Browser SpeechSynthesis, Edge TTS, NVIDIA text-to-speech, voice cloning, and other generated voices are not used. Chat answers are text-only.

Audio is served only from WAV files committed in the repository:

| Event | Recording |
|---|---|
| Welcome | `ttsfree-marathi-take2.wav` |
| Button 1 — complaints | Not uploaded yet; no audio is substituted |
| Button 2 — school information | `SCHOOLINFO.wav` |
| Button 3 — scholarship | `schoolarship.wav` |
| Button 4 — representative | `talktorep.wav` |
| Invalid input | `inavlid.wav` |
| Idle timeout | `idle.wav` |
| Return to main menu | `mainmenu.wav` |
| Goodbye | `bye.wav` |

The existing filenames are preserved exactly. The misspellings in two filenames are retained so the app can serve the files already committed; they can be renamed later if desired.

The browser demo provides controls to play the idle, invalid-input, main-menu, and goodbye recordings. Selecting buttons 2–4 plays their matching recording. Button 1 displays its text response and clearly reports that its recording is missing. The welcome recording is available in the audio player.

## API routes

- `GET /` — browser interface
- `GET /health` — health and configuration status; never returns the API key
- `GET /api/config` — model name and whether a key is configured
- `GET /api/greeting` — welcome text and recording URL
- `GET /api/audio` — prerecorded audio availability
- `GET /api/audio/{event}` — serve an allow-listed WAV recording
- `GET /api/menu` — IVR menu
- `POST /api/ivr/digit` — demo menu selection
- `POST /api/chat` — NVIDIA-powered text response only

## Safety and telephony status

This is a browser demo only. It does not connect to BSNL, a landline, SIP, PBX/EPABX, or live callers. Option 4 does not transfer a call, even though its prerecorded audio can be previewed. Do not connect it to an office phone system without office authorization and a reviewed telephony integration.

The assistant must not invent official office procedures, benefit eligibility, addresses, phone numbers, or deadlines. Verify official information with the relevant office. Do not submit Aadhaar numbers, OTPs, passwords, bank details, or sensitive personal information.


## Guided IVR menu

The browser demo now has guided submenus for all four choices:

- **1 — Complaint help:** preparing a complaint and checking its status (the demo does not submit or look up complaints).
- **2 — School information:** admission, accessibility/support, and school-related complaints.
- **3 — Scholarships:** eligibility, application guidance, and application status (no government portal is connected).
- **4 — Representative:** explains that this demo cannot transfer a call.

Submenu answers are intentionally cautious. Add verified office-specific facts only after the office approves them.

## Editing the AI system prompt

Edit `sysprompt.txt` in the project root using Notepad or another text editor. The server reads it when each AI chat request is made, so restart is not normally needed after saving. The built-in accuracy, privacy, and prototype disclaimers in `main.py` remain in force; custom instructions are appended and cannot replace those rules.

Do not put API keys, passwords, OTPs, or personal data in this file.
