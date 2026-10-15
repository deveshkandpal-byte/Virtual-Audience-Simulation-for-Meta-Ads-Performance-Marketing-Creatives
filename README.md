# Virtual Audience Simulation for Meta Ads Creatives

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/deveshkandpal-byte/Virtual-Audience-Simulation-for-Meta-Ads-Performance-Marketing-Creatives)

A beginner-friendly MVP for reviewing Meta (Facebook/Instagram) ad copy and image creatives before a live campaign. It provides a structured report, audience-response hypotheses, prioritized recommendations, JSON export, and conservative copy-optimization suggestions.

> **Important limitation:** this is a pre-launch review assistant, not a real audience panel or a validated predictive model. It cannot guarantee CTR, conversions, or ROAS. With no API key configured, analysis uses basic local rules and copy optimization gives conservative guidance only.

## Current MVP capabilities

- Campaign context: optional industry, objective, audience, offer, CTA, and landing-page URL.
- Automatic industry classification using supplied campaign details and a structured strategy library.
- Industry-specific recommendations for creative formats, messaging angles, CTA options, offer tests, funnel stage, and compliance guardrails across e-commerce, beauty, food, real estate, SaaS, education, local services, healthcare, Ayurveda/wellness, fashion, travel, B2B, finance, automotive, home, recruitment, and legal services.
- Optional public HTTPS landing-page static-text extraction (title, metadata, headings, text excerpt) with ad-to-page keyword overlap and explicit disclosure of untested checks.
- Automatic report enrichment with industry strategy, landing-page review, risk flags, evidence gaps, copy concept templates, and an objective-aligned test plan.
- Reusable system prompt, logical agent role instructions, and a separate industry-strategy skill.
- Creative review for supplied copy and JPEG, PNG, or WebP images (maximum 8 MB, validated image decoding, and a 25-megapixel pixel limit).
- A creative-type selector covering the full format/concept taxonomy in the Master Prompt, including static images, video concepts, UGC, carousels, collection/catalog, social proof, comparison/education, promotion/conversion, storytelling, and industry-specific styles.
- Format-specific checklists for image, video-script, carousel, catalog, testimonial/social-proof, educational/comparison, promotional, storytelling, and industry-style concepts. Checklists clearly disclose missing media or evidence.
- Structured report with the Master Prompt's core fields: creative type, components, simulated performance labels, strengths, weaknesses, recommended modifications, and overall assessment.
- Audience-response hypotheses and a prioritized action plan.
- Copy optimization suggestions. A configured OpenAI-compatible API can generate AI-assisted copy suggestions; without one, the app returns local guidance.
- Copy or download the report as JSON.
- Compare 2–10 copy variants under shared campaign context using a separate readiness/completeness report (does not predict a winner).
- Health endpoint at `/health`, automated tests, and GitHub Actions CI.

## Strategy knowledge, system prompt and agent skills

- [Industry strategy playbook](docs/INDUSTRY_STRATEGY_PLAYBOOK.md) — format, hook, copy, CTA, offer and funnel starting hypotheses by industry.
- [Structured industry strategy library](app/industry_strategies.json) — used by the app for automatic industry classification and recommendations.
- [System prompt](prompts/SYSTEM_PROMPT.md) and [logical agent roles](prompts/AGENT_ROLES.md) — the current app runs these roles as one orchestrated model call, not as separate autonomous agents.
- [Industry-strategy skill](skills/industry-strategy/SKILL.md) and [core simulation skill](skills/virtual-audience-simulation/SKILL.md).

A compatible AI provider is needed for custom AI-written copy variants and actual image interpretation. Without a key, the app returns industry-based guidance and clearly marked fill-in concept templates, not finished AI-generated creatives.

## Not implemented yet

- Direct video upload or video-frame/audio analysis. Script-only video/UGC checklist guidance is available, but the app does not inspect rendered video, audio, or real retention.
- A separate uploaded multi-image carousel/card-sequence inspector; carousel guidance is currently checklist-based unless its cards are individually supplied and inspected.
- Actual virtual human participants, eye-tracking, or measured audience experiments.
- A predictive model trained and validated on historical Meta Ads campaign data.
- Visual asset generation or automatic image/video editing.
- Direct publishing or export into Meta Ads Manager.

These are potential future phases, not current features. The app must not describe simulated labels as actual campaign results.

## Local installation on any computer

For the full beginner-friendly Windows, macOS, Linux, and Docker instructions, open [LOCAL_SETUP.md](LOCAL_SETUP.md). Windows users can use the one-click scripts below. The Docker Compose setup binds to `127.0.0.1` so it is not intentionally exposed to the local network.

## Quick start on Windows (beginner guide)

For the simplest setup, download the repository ZIP and extract it. Double-click **`install_windows.bat`** once to install dependencies, then double-click **`run_windows.bat`** whenever you want to start the app. The app opens at `http://127.0.0.1:8000`; keep its terminal window open while using it. If Windows blocks a script, follow the manual commands below.

## Run on Windows (manual guide)

You only need to do these steps once to set up the project. You do **not** need to know how to write code to follow them.

### 1. Install Python

Install Python 3.11 or newer from [python.org](https://www.python.org/downloads/). During installation, tick **Add Python to PATH** if the installer offers that option.

### 2. Download this project

On this GitHub page, click **Code → Download ZIP**, then extract the ZIP to a folder you can find easily, such as your Desktop.

### 3. Open Command Prompt in the project folder

Open the extracted folder in File Explorer, click the address bar, type `cmd`, and press Enter.

### 4. Create a virtual environment and install dependencies

Run these commands one at a time:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the first command fails, confirm Python 3.11+ is installed and available in PATH.

### 5. Start the application

```bat
uvicorn app.main:app --reload
```

Keep that Command Prompt window open while using the app.

### 6. Open the app

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. To check that the backend is running, open [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

To stop the app, return to Command Prompt and press **Ctrl+C**.

## Optional: enable AI-assisted review

The app can use an OpenAI-compatible chat-completions API for text analysis and image review. This requires a valid provider API key and may incur provider charges. The API key is **not** included in this repository.

Use `.env.example` as a reference for the variable names. The application does **not** automatically load `.env` files, so you do not need to create one for the basic setup. Before starting the app in Windows Command Prompt, set the variables in that same terminal session:

```bat
set OPENAI_API_KEY=your_key_here
set OPENAI_BASE_URL=https://api.openai.com/v1
set OPENAI_MODEL=gpt-4o-mini
uvicorn app.main:app --reload
```

Replace `your_key_here` with your own secret. Do not paste it into public issues, chat messages, or source files. Check your provider's model and image-input support before use. If you do not configure a provider, the app still runs in local heuristic mode.

## Full creative-type library and AI-agent skill

- [Complete creative types, concepts, and format-specific review criteria](docs/CREATIVE_TYPE_LIBRARY.md)
- [Portable AI-agent skill](skills/virtual-audience-simulation/SKILL.md)
- [Local Windows and AI-agent skill setup guide](AGENT_SETUP.md)

The skill is a reusable instruction file, not a binary plugin. Agent compatibility and skill discovery vary; users may need to copy it into the agent's documented skills directory or explicitly ask the agent to read it. A skill does not itself grant shell, browser, model, or API access.

## Using the app

1. Select the creative format and campaign objective.
2. Enter any known heading/hook, ad copy or script, offer, CTA, destination, and target audience.
3. Optionally attach a JPEG, PNG, or WebP image.
4. Select **Analyze this creative**.
5. Review strengths, weaknesses, audience-response hypotheses, and the prioritized action plan.
6. Select **Generate copy fixes** for alternative copy guidance.
7. Copy or download the structured JSON report.

You can leave fields blank. Missing components should be reported as **Not provided** rather than invented. Video files are not supported in this MVP; for now, paste the video script or describe the concept in the text fields. Video/UGC creative types receive a script-only checklist for the opening hook, pacing cues, visual directions, audio/subtitles, and closing CTA. These are editorial checks, not video measurements.

### Compare variants

1. Scroll to **Compare creative variants**.
2. Enter the same campaign objective and audience for all variants.
3. Fill in 2–10 variants with their name, hook, copy, offer, CTA, and destination.
4. Select **Compare variants** and review the JSON summary and testing plan.
5. Select **Download comparison JSON** to save the report.

The comparison flags input completeness; it does not predict a winner or estimate live ad results.

## Run the tests

From the project folder, with the virtual environment activated:

```bat
python -m pytest -q
```

GitHub Actions also runs the test suite when changes are pushed to `main` or a pull request targets `main`.

## Privacy and safety notes

- Uploaded images are processed in memory by the application; this MVP does not intentionally save them to a user-upload directory.
- If an AI provider is configured, the submitted campaign text and attached image may be sent to that provider for processing. Review the provider's data policy before using sensitive client material.
- Do not submit secrets, private customer information, or campaign information you are not authorized to share.
- File extensions and browser-provided MIME types are not a complete security boundary. Do not expose an unreviewed development instance publicly.
- Use only substantiated claims, genuine testimonials, and confirmed offers in ad copy.

## Publish a public demo (Render)

This repository includes a `render.yaml` blueprint for a **no-secret demo**. It intentionally does not configure a paid AI API key, so the public demo uses local heuristic analysis and script/copy guidance unless the owner separately configures an AI provider.

1. First change this GitHub repository to **Public** (see the repository's **Settings → General → Danger Zone → Change visibility**).
2. Sign in to [Render](https://render.com/) and connect your GitHub account.
3. In Render, choose **New → Blueprint** and select this repository.
4. Review the service settings from `render.yaml` and create the service.
5. Wait for the deployment to finish, then open the generated `onrender.com` URL and check `/health`.

Render's free-plan availability, account requirements, and service behavior can change. A free web service may sleep after inactivity. The generated public URL is created by Render; it is not known until you deploy.

**Public-demo safety:** the app includes a simple in-memory per-IP request throttle, but this is not production-grade abuse protection. Do not add a paid AI API key to a public demo without adding authentication, quotas, monitoring, and stronger rate limiting. Do not submit confidential client creatives or sensitive campaign information. The app has not undergone an independent security review.

## Open-source license

This project is released under the [MIT License](LICENSE). Contributions and issue reports are welcome; see [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## Technology

- Python 3.11
- FastAPI and Uvicorn
- Plain HTML, CSS, and JavaScript frontend
- Pytest and FastAPI TestClient
- Optional OpenAI-compatible API configuration

## Roadmap

1. Strengthen formal response-schema validation and provider-failure tests.
2. Add direct video upload and multimodal analysis only after choosing and testing a suitable provider.
3. Add visual asset generation as a separate, reviewable workflow.
4. Add deployment, rate limiting, authentication, and privacy controls before hosting a public instance.
5. Consider numerical performance estimation only after obtaining permitted historical campaign data and validating the model on held-out data.

## Project status

**Early MVP under active development.** The audit report is available in [AUDIT.md](AUDIT.md). Validate all suggestions and test promising variants with controlled live campaigns before making budget decisions.
