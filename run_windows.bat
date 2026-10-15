@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo The app is not installed yet. Double-click install_windows.bat first.
  pause
  exit /b 1
)
echo Starting Virtual Audience Simulation...
echo Open http://127.0.0.1:8000 in your browser.
echo Keep this window open while using the app. Press Ctrl+C to stop.
".venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
pause
