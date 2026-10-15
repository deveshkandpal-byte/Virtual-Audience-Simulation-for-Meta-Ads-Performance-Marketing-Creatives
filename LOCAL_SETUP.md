# Local installation guide

This guide explains how to run the app on your own computer. You do not need to edit application code.

## Choose a setup method

- **Windows, easiest:** download/extract the GitHub ZIP, double-click `install_windows.bat` once, then `run_windows.bat` each time you want to use the app.
- **Windows/macOS/Linux, manual Python:** follow the steps below.
- **Docker:** use `compose.yaml` if Docker Desktop (Windows/macOS) or Docker Engine + Compose (Linux) is already installed.
- **AI-agent skill only:** see [AGENT_SETUP.md](AGENT_SETUP.md); this does not require running the web app.

## Method 1 — Windows quick start

1. Install Python 3.11+ from https://www.python.org/downloads/.
2. Download this repository using GitHub **Code → Download ZIP** and extract it.
3. Double-click `install_windows.bat` and wait for it to finish.
4. Double-click `run_windows.bat`.
5. Open http://127.0.0.1:8000 in your browser. Keep the black terminal window open while using the app.
6. To stop it, focus the terminal and press Ctrl+C.

If the scripts fail, use Method 2 and read the error message in the terminal.

## Method 2 — Python setup

Install Python 3.11 or newer, download/extract the repository, then open a terminal in the project folder.

### Windows Command Prompt

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. The API health check is http://127.0.0.1:8000/health and interactive API docs are at http://127.0.0.1:8000/docs. Keep the terminal running while you use the app. Press Ctrl+C to stop it.

For the next session, open a terminal in the project folder and activate the environment:
- Windows: `.venv\Scripts\activate`
- macOS/Linux: `source .venv/bin/activate`

Then run `python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`.

### If port 8000 is already in use

Change the last command to use port 8001 and open http://127.0.0.1:8001.

## Method 3 — Docker Compose

1. Install Docker Desktop (Windows/macOS) or Docker Engine with Compose (Linux).
2. Open a terminal in the repository folder.
3. Build and start the app:

```bash
docker compose up --build
```

4. Open http://127.0.0.1:8000.
5. Stop it with Ctrl+C. To stop and remove the container, run `docker compose down`.

The Compose configuration binds the app to the local loopback interface, not all network interfaces. It does not require an AI API key. If you intentionally configure an AI provider, set the environment variables in your shell before starting Compose. Never commit real secrets into the repository.

## Local analysis versus AI-assisted analysis

- **No API key:** the app uses rule-based local checks. This is not a trained audience simulator and does not predict actual CTR, conversions, or ROAS.
- **With a supported API key:** the app can send the supplied campaign text and image to the configured external provider. This may incur charges and is subject to that provider's data policy.
- The app does not automatically load `.env` in the Python/manual setup. In Windows Command Prompt, set variables in that same window before launching:

```bat
set OPENAI_API_KEY=your_key_here
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Do not replace the placeholder in any shared file; use your actual key only in your own terminal/session. For Docker Compose, shell environment variables are passed through by `compose.yaml`.

## Test the installation

With the Python virtual environment activated:

```bash
python -m pytest -q
```

Check that the home page loads and `/health` returns JSON containing `"status": "ok"`.

## Troubleshooting

- **Python command not found:** install Python 3.11+ and reopen your terminal.
- **Dependency install fails:** check your internet connection, activate the virtual environment, and retry `python -m pip install -r requirements.txt`.
- **Browser says it cannot connect:** confirm the terminal still shows the server running and use the exact port printed in your command.
- **Image is rejected:** upload a real JPEG, PNG, or WebP file under 8 MB, or MP4/MOV/WebM video under 25 MB. Renaming a different file does not convert it. Video review samples up to eight frames from the first 30 seconds; audio and continuous motion are not analyzed.
- **Image is not visually described:** expected in local heuristic mode without a compatible vision-enabled provider.
- **AI provider errors:** confirm the key, base URL, model name, billing, and image-input support. The app falls back to local guidance when provider review fails.
- **Agent cannot find its skill:** use the separate [AI-agent skill guide](AGENT_SETUP.md) and the agent product's current skill-directory documentation.

## Safety and privacy

The app is intended for local use by default. Do not expose it to the public internet without authentication, production-grade rate limiting, logging/monitoring, and a security review. If an AI provider is configured, text and images may leave your computer and be processed by that provider. Do not upload confidential client assets unless you are authorized to do so.
