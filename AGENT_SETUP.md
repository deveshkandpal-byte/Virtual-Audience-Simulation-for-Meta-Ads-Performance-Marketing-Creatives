# Local installation and AI-agent skill setup

This guide is for non-developers. The application and the reusable agent skill are separate things: the app is a local web tool; the skill is a set of instructions another AI agent can follow.

## Part A — Run the application on Windows

1. Install Python 3.11 or newer from https://www.python.org/downloads/. Enable **Add Python to PATH** if offered.
2. Open this repository on GitHub and choose **Code → Download ZIP**. Extract it.
3. Open the extracted folder in File Explorer. Click the address bar, type `cmd`, and press Enter.
4. Run these commands one at a time:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

5. Keep the terminal open and open http://127.0.0.1:8000 in a browser.
6. Health check: http://127.0.0.1:8000/health. API documentation: http://127.0.0.1:8000/docs.
7. To stop the app, return to the terminal and press Ctrl+C. Next time, open the project folder's terminal, run `.venv\Scripts\activate`, then `uvicorn app.main:app --reload`.

If `py -3` is not recognized, install Python 3.11+ and reopen Command Prompt. If port 8000 is already in use, run `uvicorn app.main:app --reload --port 8001` and open http://127.0.0.1:8001.

### Optional AI provider

Without an API key, the app runs local heuristic analysis. Image understanding and AI-assisted text review require a compatible provider and may cost money. The app does **not** automatically load `.env`; set variables in the same terminal before starting it:

```bat
set OPENAI_API_KEY=your_key_here
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
uvicorn app.main:app --reload
```

Replace the example key locally. Never commit keys or paste them into public issues. Check your provider's supported model, image input, billing, and data policy. Do not expose a paid API key through an unauthenticated public deployment.

## Part B — Install the reusable skill in an AI agent

The portable skills live at `skills/virtual-audience-simulation/SKILL.md` and `skills/industry-strategy/SKILL.md`. The system prompt and logical agent-role instructions live in `prompts/SYSTEM_PROMPT.md` and `prompts/AGENT_ROLES.md`; the industry playbook and structured library are in `docs/INDUSTRY_STRATEGY_PLAYBOOK.md` and `app/industry_strategies.json`. It can be read by an AI agent even when the web app is not running. Keep the whole repository available if the agent needs the detailed taxonomy in `docs/CREATIVE_TYPE_LIBRARY.md`.

1. Download or clone this repository.
2. Copy the `skills/virtual-audience-simulation` and `skills/industry-strategy` folders into the agent's supported skills directory. Keep `docs/INDUSTRY_STRATEGY_PLAYBOOK.md`, `docs/CREATIVE_TYPE_LIBRARY.md`, `app/industry_strategies.json` and `prompts/` available as references.
3. If the agent supports the Agent Skills format, it should recognize `SKILL.md` with YAML frontmatter. If it does not auto-discover skills, ask it to read that file explicitly.
4. Keep `docs/CREATIVE_TYPE_LIBRARY.md` alongside the skill, or copy its taxonomy into the agent's project knowledge. The skill references it.
5. Give the agent a creative, objective, audience, offer, CTA, and destination; ask it to follow the skill and return valid JSON.
6. If you want the agent to call the local web app rather than review directly, the agent must have local tool/terminal or HTTP access. Start the app first and expose it only to trusted local tools.

### Where to put it

Agent skill discovery differs by product and version. Use the location documented by your specific agent; do not assume every agent scans the same folder.

- **Portable repository copy:** `skills/virtual-audience-simulation/SKILL.md`
- **Claude Code:** commonly `.claude/skills/virtual-audience-simulation/SKILL.md` inside a project, or the user-level skills folder supported by your installed version.
- **Other agents/editors:** use their documented custom-skills or project-instructions mechanism. If they do not support skills, paste the contents of `SKILL.md` into the agent's project instructions or ask it to read the file.

This is a reusable instruction skill, not a plugin binary. Copying it does not automatically give an agent a shell, browser, API key, model access, or the ability to run the app. Those permissions must be configured separately by you.

## Part C — Validate the setup

From the project folder, activate the virtual environment and run:

```bat
python -m pytest -q
```

Then check the browser app and `/health`. For agent-only use, ask the agent to summarize the supported creative categories and return one valid JSON review. Confirm it states uncertainty and does not fabricate results.

## Troubleshooting

- **App will not start:** check Python version, activate `.venv`, and run `pip install -r requirements.txt` again.
- **Image review says no vision provider:** expected in local heuristic mode; configure a compatible vision-enabled provider if needed.
- **Agent cannot find the skill:** check the agent's official skill directory and reload/restart its session, or explicitly ask it to read `SKILL.md`.
- **Agent returns invented metrics:** tell it to follow the metric-integrity section in the skill and use qualitative estimates when no validated basis exists.
- **Port is occupied:** use `--port 8001` and open the matching localhost URL.

See `README.md` and `SECURITY.md` for more details. Do not send private client creatives to a third-party AI provider unless authorized.
