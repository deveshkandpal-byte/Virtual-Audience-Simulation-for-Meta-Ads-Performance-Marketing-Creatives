@echo off
setlocal
cd /d "%~dp0"
echo ================================================
echo Virtual Audience Simulation - Windows Setup
echo ================================================
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher was not found.
  echo Install Python 3.11 or newer from https://www.python.org/downloads/
  echo Reopen this window after installation and try again.
  pause
  exit /b 1
)
py -3 -c "import sys; raise SystemExit(sys.version_info < (3, 11))" >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python 3.11 or newer was not found.
  echo Install Python 3.11 or newer and ensure the Python Launcher is enabled.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Creating local virtual environment...
  py -3 -m venv .venv
  if errorlevel 1 goto failed
)
echo Installing/updating dependencies...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Setup complete. Double-click run_windows.bat to start the app.
pause
exit /b 0
:failed
echo.
echo Setup failed. Check your internet connection and Python installation.
pause
exit /b 1
