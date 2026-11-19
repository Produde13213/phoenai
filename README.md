# PhoenAI — Marathi IVR Prototype

A small FastAPI + browser prototype for a Marathi-language IVR menu. It uses the repository's `ttsfree-marathi-take2.wav` file as the welcome recording.

## Important

This is a **browser demo only**. It does not connect to a telephone number, BSNL line, PBX/EPABX, SIP trunk, or live callers. Option 4 does not transfer a call; it explains that transfer is not configured. Do not connect it to a real office phone system without the office's authorization and a properly reviewed telephony integration.

## Run on Windows

1. Install Python 3.10 or newer.
2. Open PowerShell in this repository.
3. Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run the app using the venv executable directly instead.

4. Install dependencies and start the server:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

5. Open http://127.0.0.1:8000 in your browser.

## API

- `GET /health` — service status
- `GET /api/greeting` — Marathi welcome text and audio availability
- `GET /api/greeting/audio` — welcome WAV recording
- `GET /api/menu` — menu options
- `POST /api/ivr/digit` — choose an option, JSON body such as `{"digit":"1"}`

## Project layout

```text
.
├── main.py
├── requirements.txt
├── ttsfree-marathi-take2.wav
└── static/
    └── index.html
```

The browser uses the speech synthesis voices available on the user's device for spoken menu responses. Marathi voice availability depends on the browser and operating system.
