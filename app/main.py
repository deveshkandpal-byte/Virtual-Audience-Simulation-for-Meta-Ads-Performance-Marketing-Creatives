import base64
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent
MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(
    title="Virtual Audience Simulation for Meta Ads Creatives",
    description="Pre-launch creative review. Outputs are simulated hypotheses, not live Meta Ads results.",
    version="0.1.0",
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "virtual-audience-simulation", "version": "0.1.0"}


def _rating(text: str, terms: tuple[str, ...]) -> str:
    normalized = text.lower()
    hits = sum(1 for term in terms if term in normalized)
    return "Medium" if hits >= 2 else ("Low" if hits == 0 else "Medium")


def heuristic_report(data: dict[str, str], image_attached: bool, image_inspected: bool = False) -> dict[str, Any]:
    """Conservative local fallback; never pretends to be a trained predictive model."""
    heading = data.get("heading", "").strip() or "Not provided"
    ad_copy = data.get("ad_copy", "").strip() or "Not provided"
    offer = data.get("offer", "").strip() or "Not provided"
    cta = data.get("cta", "").strip() or "Not provided"
    visual_text = "Image attached; visual inspection unavailable in local heuristic mode." if image_attached else "Not provided"
    if image_inspected:
        visual_text = "Image supplied for AI visual review."
    all_copy = " ".join([heading, ad_copy, offer, cta])
    weaknesses: list[str] = []
    strengths: list[str] = []
    mods: list[dict[str, str]] = []

    if heading == "Not provided":
        weaknesses.append("No heading was supplied, so stopping power and message clarity cannot be assessed.")
        mods.append({"component": "heading", "suggestion": "Add a specific, audience-relevant headline based on a verified product benefit."})
    elif len(heading) > 90:
        weaknesses.append("The heading is relatively long and may be harder to scan quickly on mobile placements.")
        mods.append({"component": "heading", "suggestion": "Test a shorter headline that communicates one specific benefit."})
    else:
        strengths.append("A heading was supplied and can be evaluated against the campaign objective.")

    if ad_copy == "Not provided":
        weaknesses.append("Ad copy was not supplied, limiting assessment of relevance, objections, and persuasion.")
        mods.append({"component": "ad_copy", "suggestion": "Add the primary text, explain the real offer, and address one relevant audience objection."})
    elif len(ad_copy.split()) < 12:
        strengths.append("The copy is concise, which may help mobile readability.")
        mods.append({"component": "ad_copy", "suggestion": "Check whether the concise copy still explains the product, its verified benefit, and why the audience should care."})
    else:
        strengths.append("Ad copy is present, allowing its message and relevance to be reviewed.")

    if offer == "Not provided":
        weaknesses.append("The offer is missing or unclear; perceived value cannot be judged.")
        mods.append({"component": "offer", "suggestion": "State the actual product/service and any verified price or offer. Do not add unconfirmed discounts or urgency."})
    else:
        strengths.append("An offer or product proposition was supplied for review.")

    if cta == "Not provided":
        weaknesses.append("No CTA was supplied, so the intended next step is unclear.")
        mods.append({"component": "cta", "suggestion": "Add one visible CTA that matches the campaign objective and destination."})
    else:
        strengths.append("A CTA was supplied; verify that it matches the destination and campaign goal.")

    if re.search(r"\b(guaranteed|100% results|cure|double your income|instant results)\b", all_copy, re.I):
        weaknesses.append("Copy includes a potentially absolute or high-risk claim that needs substantiation and policy review.")
        mods.append({"component": "trust_signals", "suggestion": "Substantiate strong claims or replace them with accurate, qualified wording supported by evidence."})

    objective = data.get("objective", "Sales").strip() or "Not provided"
    audience = data.get("audience", "").strip() or "Not provided"
    destination = data.get("destination", "").strip() or "Not provided"
    if destination == "Not provided":
        mods.append({"component": "landing_page", "suggestion": "Provide the destination or conversion path to assess message consistency and conversion friction."})
    if not mods:
        mods.append({"component": "audience_fit", "suggestion": "Test a second hook or message angle while keeping audience, offer, and objective consistent."})

    report = {
        "creative_type": data.get("creative_type", "Not provided"),
        "components": {"heading": heading, "ad_copy": ad_copy, "offer": offer, "cta": cta},
        "simulated_performance": {
            "engagement_rate": _rating(all_copy, ("benefit", "problem", "why", "you", "discover", "save", "learn")),
            "ctr": "Medium" if cta != "Not provided" and heading != "Not provided" else "Low",
            "conversion_rate": "Not enough information for a defensible estimate",
        },
        "analysis": {
            "strengths": strengths or ["No reliable strengths can be confirmed from the supplied information yet."],
            "weaknesses": weaknesses or ["No obvious copy-level issue was detected by the basic local checks; this is not proof of strong performance."],
        },
        "recommended_modifications": mods,
        "overall_assessment": "Requires major modifications" if len(weaknesses) >= 3 else ("Requires minor modifications" if weaknesses else "Ready for controlled testing"),
        "audience_responses": [
            {"segment": "Cold audience", "likely_reaction": "May need a clear product explanation and reason to stop scrolling.", "confidence": "Low; heuristic, not observed user data."},
            {"segment": "Problem-aware audience", "likely_reaction": "Relevance depends on whether the copy clearly reflects a real need and substantiated benefit.", "confidence": "Low; heuristic, not observed user data."},
            {"segment": "Warm / high-intent audience", "likely_reaction": "May need a clear offer, trust evidence, and a low-friction next step.", "confidence": "Low; heuristic, not observed user data."},
        ],
        "action_plan": [
            {"priority": "Priority 1 — Critical", "action": mods[0]["suggestion"]},
            {"priority": "Priority 2 — High Impact", "action": "Align the creative message, offer, CTA, campaign objective, and destination."},
            {"priority": "Priority 3 — Testing Opportunities", "action": "Test one alternative hook or headline at a time; validate with a controlled live campaign."},
        ],
        "context": {"campaign_objective": objective, "target_audience": audience, "destination": destination},
        "simulation_notice": "This is a local rule-based review, not an AI audience panel, trained predictive model, or actual Meta Ads result.",
        "visual_review_notice": (
            "The uploaded image was not visually inspected because no AI provider is configured."
            if image_attached and not image_inspected
            else ("An image was included in the configured AI review." if image_inspected else "No image was supplied.")
        ),
    }
    return report


def _call_vision_model(data: dict[str, str], image_bytes: bytes | None, image_type: str | None) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("No API key configured; using local heuristic mode.")
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip()
    system_prompt = """You review Meta Ads creatives for performance marketers. Analyze the provided facts only.
Return exactly one valid JSON object. Required keys: creative_type (string), components (heading, ad_copy, offer, cta strings), simulated_performance (engagement_rate, ctr, conversion_rate strings), analysis (strengths and weaknesses arrays of strings), recommended_modifications (array of objects with component and suggestion strings), overall_assessment (one of: Ready for controlled testing, Requires minor modifications, Requires major modifications, Not recommended in its current form). You may add audience_responses (array of objects), action_plan (array of objects with priority and action), context, simulation_notice, visual_review_notice.
Never invent product facts, discounts, guarantees, testimonials, deadlines, or outcomes. Missing components must say Not provided. Do not claim metrics are actual results or reliably predict CTR, conversion, or ROAS. Prefer qualitative ratings; if evidence is insufficient, say so. Explain assumptions and uncertainty. Do not assume one ad format always wins. Evaluate relevant audience fit, hook, heading, copy, offer, CTA, visual, trust signals, destination, pacing/subtitles/audio if video details are provided. For multiple creatives, this endpoint handles one creative at a time; do not invent a comparison."""
    user_payload = {
        "creative_type": data.get("creative_type", "Not provided"),
        "heading": data.get("heading", "").strip() or "Not provided",
        "ad_copy": data.get("ad_copy", "").strip() or "Not provided",
        "offer": data.get("offer", "").strip() or "Not provided",
        "cta": data.get("cta", "").strip() or "Not provided",
        "campaign_objective": data.get("objective", "Not provided"),
        "target_audience": data.get("audience", "").strip() or "Not provided",
        "destination": data.get("destination", "").strip() or "Not provided",
        "instructions": "Use the Master Prompt principles. State when the evidence does not support a conclusion. Return the report JSON only.",
    }
    content: list[dict[str, Any]] = [{"type": "text", "text": json.dumps(user_payload, ensure_ascii=False)}]
    if image_bytes is not None and image_type is not None:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        content.append({"type": "image_url", "image_url": {"url": f"data:{image_type};base64,{encoded}"}})
    body = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content}],
    }
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        raw = result["choices"][0]["message"]["content"]
        report = json.loads(raw)
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"AI provider request failed: {exc}") from exc

    required = {"creative_type", "components", "simulated_performance", "analysis", "recommended_modifications", "overall_assessment"}
    if not isinstance(report, dict) or not required.issubset(report):
        raise RuntimeError("AI provider returned a report that does not match the required structure.")
    for key in ("heading", "ad_copy", "offer", "cta"):
        report.setdefault("components", {}).setdefault(key, user_payload.get(key, "Not provided"))
    report["simulation_notice"] = "AI-generated simulated assessment only. These are hypotheses, not actual Meta Ads results or validated performance predictions."
    report["visual_review_notice"] = "Image submitted to the configured AI provider for visual review." if image_bytes else "No image was supplied."
    report.setdefault("context", {
        "campaign_objective": user_payload["campaign_objective"],
        "target_audience": user_payload["target_audience"],
        "destination": user_payload["destination"],
    })
    report.setdefault("audience_responses", [])
    report.setdefault("action_plan", [])
    return report


@app.post("/api/analyze")
async def analyze(
    creative_type: str = Form("Static Image — Ad Copy Review"),
    heading: str = Form(""),
    ad_copy: str = Form(""),
    offer: str = Form(""),
    cta: str = Form(""),
    objective: str = Form("Sales"),
    audience: str = Form(""),
    destination: str = Form(""),
    creative_file: UploadFile | None = File(None),
) -> dict[str, Any]:
    data = {
        "creative_type": creative_type.strip() or "Not provided",
        "heading": heading[:1000],
        "ad_copy": ad_copy[:12000],
        "offer": offer[:3000],
        "cta": cta[:1000],
        "objective": objective[:300],
        "audience": audience[:2000],
        "destination": destination[:2000],
    }
    image_bytes = None
    image_type = None
    if creative_file and creative_file.filename:
        image_type = (creative_file.content_type or "").lower()
        if image_type.startswith("video/"):
            raise HTTPException(status_code=415, detail="Video upload is not supported in this MVP. You can currently analyze ad copy and JPEG, PNG, or WebP images. Video analysis is a planned next step.")
        if image_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=415, detail="Unsupported file type. Upload a JPEG, PNG, or WebP image.")
        image_bytes = await creative_file.read(MAX_IMAGE_BYTES + 1)
        if len(image_bytes) > MAX_IMAGE_BYTES:
            raise HTTPException(status_code=413, detail="Image is larger than the 8 MB limit.")
        if not image_bytes:
            image_bytes = None

    try:
        if os.getenv("OPENAI_API_KEY", "").strip():
            report = _call_vision_model(data, image_bytes, image_type)
            report["analysis_mode"] = "configured_ai"
        else:
            report = heuristic_report(data, image_attached=image_bytes is not None)
            report["analysis_mode"] = "local_heuristic"
    except RuntimeError as exc:
        report = heuristic_report(data, image_attached=image_bytes is not None)
        report["analysis_mode"] = "local_heuristic"
        report["provider_note"] = str(exc)
    return report


def heuristic_optimization(data: dict[str, str]) -> dict[str, Any]:
    """Suggest safer, clearer copy without inventing product claims or offers."""
    heading = data.get("heading", "").strip()
    ad_copy = data.get("ad_copy", "").strip()
    offer = data.get("offer", "").strip()
    cta = data.get("cta", "").strip()
    objective = data.get("objective", "Sales").strip() or "Sales"
    return {
        "optimized_creative": {
            "heading": heading if heading else "Add a clear, specific headline based on a verified benefit",
            "ad_copy": ad_copy if ad_copy else "Add the product or service, its verified benefit, and the reason it is relevant to your audience. Replace this guidance with confirmed details before publishing.",
            "offer": offer if offer else "Not provided — add only the actual, confirmed offer or product details.",
            "cta": cta if cta else ("Send Message" if objective.lower() == "whatsapp conversations" else ("Get a Quote" if objective.lower() == "leads" else ("Learn More" if objective.lower() in {"traffic", "awareness", "engagement"} else "Shop Now")) ,
        },
        "changes": [
            {"component": "heading", "reason": "Keep the headline specific and grounded in a benefit that the business can substantiate."},
            {"component": "ad_copy", "reason": "Make the product, value, and next step clear; use only verified details."},
            {"component": "offer", "reason": "No price, discount, deadline, guarantee, or product fact is invented by this fallback."},
            {"component": "cta", "reason": "The suggested CTA is a starting point; confirm it matches the actual destination."},
        ],
        "mode": "local_guidance",
        "notice": "These are conservative copy suggestions, not generated visual assets or a performance guarantee. Review all wording and replace guidance with confirmed facts before publishing.",
    }


@app.post("/api/optimize")
async def optimize(
    creative_type: str = Form("Static Image — Ad Copy Review"),
    heading: str = Form(""),
    ad_copy: str = Form(""),
    offer: str = Form(""),
    cta: str = Form(""),
    objective: str = Form("Sales"),
    audience: str = Form(""),
    destination: str = Form(""),
) -> dict[str, Any]:
    data = {
        "creative_type": creative_type[:300],
        "heading": heading[:1000],
        "ad_copy": ad_copy[:12000],
        "offer": offer[:3000],
        "cta": cta[:1000],
        "objective": objective[:300],
        "audience": audience[:2000],
        "destination": destination[:2000],
    }
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return heuristic_optimization(data)

    system = """You are a careful performance-marketing copy editor. Return only valid JSON with keys optimized_creative (heading, ad_copy, offer, cta strings), changes (array of component and reason strings), mode, notice. Preserve verified facts. Never invent claims, prices, discounts, guarantees, testimonials, deadlines, or results. For missing input, write 'Not provided' or a clear editorial placeholder, never pretend it is a fact. Suggest copy only; do not claim to generate images or videos. State that the result is a hypothesis to review before publishing."""
    payload = {
        "creative_type": data["creative_type"],
        "heading": data["heading"] or "Not provided",
        "ad_copy": data["ad_copy"] or "Not provided",
        "offer": data["offer"] or "Not provided",
        "cta": data["cta"] or "Not provided",
        "objective": data["objective"],
        "audience": data["audience"] or "Not provided",
        "destination": data["destination"] or "Not provided",
    }
    body = {
        "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini").strip(),
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": json.dumps(payload, ensure_ascii=False)}],
    }
    req = urllib.request.Request(
        f"{os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')}/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            result = json.loads(response.read().decode("utf-8"))
        parsed = json.loads(result["choices"][0]["message"]["content"])
        creative = parsed.get("optimized_creative")
        if not isinstance(creative, dict) or not all(isinstance(creative.get(k), str) for k in ("heading", "ad_copy", "offer", "cta")):
            raise RuntimeError("AI provider returned an invalid optimized_creative structure.")
        parsed["mode"] = "configured_ai"
        parsed["notice"] = "AI-assisted copy suggestions only. Review every claim and confirm the offer before publishing; no performance outcome is guaranteed."
        return parsed
    except (urllib.error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError, RuntimeError) as exc:
        fallback = heuristic_optimization(data)
        fallback["provider_note"] = f"AI copy optimization was unavailable; local guidance was returned. Details: {exc}"
        return fallback
