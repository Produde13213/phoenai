@echo off
setlocal
cd /d "%~dp0"

echo.
echo  PhoenAI - Marathi IVR Browser Demo
echo  ----------------------------------
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3 -m venv .venv
    if errorlevel 1 (
        echo Could not create the virtual environment. Install Python 3.11 or newer first.
        pause
        exit /b 1
    )
)

echo Checking required Python packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Package installation failed. Check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo Starting PhoenAI at http://127.0.0.1:8000
echo Keep this window open while presenting the demo.
echo Press Ctrl+C to stop the server.
echo.

start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn main:app --host 127.0.0.1 --port 8000
pause
