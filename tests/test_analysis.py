import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app, heuristic_report
from app.strategy_engine import build_strategy_context, detect_industry, fetch_landing_page, load_strategy_library

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_missing_components_are_not_invented():
    report = heuristic_report(
        {"creative_type": "Static Image", "heading": "", "ad_copy": "", "offer": "", "cta": ""},
        image_attached=False,
    )
    assert report["components"]["heading"] == "Not provided"
    assert report["components"]["ad_copy"] == "Not provided"
    assert report["components"]["offer"] == "Not provided"
    assert report["components"]["cta"] == "Not provided"
    assert "not an AI audience panel" in report["simulation_notice"]


def test_local_report_has_master_prompt_fields():
    report = heuristic_report(
        {
            "creative_type": "Static Image",
            "heading": "A better workflow",
            "ad_copy": "Learn how this tool can simplify your weekly work and save time.",
            "offer": "Software demo",
            "cta": "Learn More",
            "objective": "Leads",
            "audience": "Small business owners",
        },
        image_attached=False,
    )
    for key in ("creative_type", "components", "simulated_performance", "analysis", "recommended_modifications", "overall_assessment"):
        assert key in report
    assert set(("heading", "ad_copy", "offer", "cta")).issubset(report["components"])
    assert set(("engagement_rate", "ctr", "conversion_rate")).issubset(report["simulated_performance"])
    assert "action_plan" in report
    assert "audience_responses" in report


def test_invalid_video_upload_is_rejected_with_explanation():
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Video — Product demonstration", "objective": "Sales"},
        files={"creative_file": ("sample.mp4", b"not-a-real-video", "video/mp4")},
    )
    assert response.status_code == 415
    assert "could not be decoded" in response.json()["detail"] or "No readable video frames" in response.json()["detail"]


def test_unsupported_file_type_is_rejected():
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image"},
        files={"creative_file": ("sample.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 415



def test_optimize_endpoint_returns_safe_local_guidance_without_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/api/optimize",
        data={
            "creative_type": "Static Image",
            "heading": "A smarter workflow",
            "ad_copy": "Try our service to simplify your work.",
            "offer": "",
            "cta": "",
            "objective": "Leads",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "local_guidance"
    assert body["optimized_creative"]["heading"] == "A smarter workflow"
    assert body["optimized_creative"]["offer"].startswith("Not provided")
    assert body["optimized_creative"]["cta"] == "Get a Quote"
    assert "performance guarantee" in body["notice"]


def test_analysis_marks_missing_fields_and_does_not_claim_live_results():
    response = client.post("/api/analyze", data={"creative_type": "Static Image"})
    assert response.status_code == 200
    body = response.json()
    assert body["components"]["heading"] == "Not provided"
    assert "not an AI audience panel" in body["simulation_notice"]
    assert body["simulated_performance"]["conversion_rate"] == "Not enough information for a defensible estimate"



def test_image_with_mismatched_content_signature_is_rejected():
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image"},
        files={"creative_file": ("fake.png", b"this is not a PNG", "image/png")},
    )
    assert response.status_code == 415
    assert "contents do not match" in response.json()["detail"]



def test_comparison_endpoint_returns_individual_reports_and_disclaimer():
    response = client.post(
        "/api/compare",
        json={
            "objective": "Sales",
            "audience": "Urban professionals",
            "creatives": [
                {"name": "Variant A", "heading": "Lunch made easy", "ad_copy": "Explore lunch options for your office team.", "offer": "Menu varies", "cta": "Learn More", "destination": "Website"},
                {"name": "Variant B", "heading": "Office lunch options", "ad_copy": "See available lunch choices for your team.", "offer": "", "cta": "Learn More", "destination": "Website"},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["creative_count"] == 2
    assert len(body["individual_reports"]) == 2
    assert "component_completeness" in body["comparative_summary"]
    assert "does not identify a performance winner" in body["comparative_summary"]["interpretation"]
    assert "No variant is declared the performance winner" in body["disclaimer"]


def test_comparison_requires_at_least_two_creatives():
    response = client.post("/api/compare", json={"creatives": [{"name": "Only one"}]})
    assert response.status_code == 422



def test_video_script_review_is_labeled_as_script_only():
    report = heuristic_report(
        {
            "creative_type": "Video — Concept / Script Review (no video upload)",
            "heading": "Stop scrolling",
            "ad_copy": "Stop scrolling. See how the product works. Scene: show the package. End with a clear CTA.",
            "offer": "Not provided",
            "cta": "Learn More",
            "objective": "Sales",
            "audience": "Food delivery customers",
            "destination": "Website",
        },
        image_attached=False,
    )
    assert report["video_script_checks"]["scope"].startswith("Script/concept only")
    assert "actual viewer retention is not measured" in report["video_script_checks"]["first_3_seconds"]
    assert report["video_script_checks"]["closing_cta"] == "Learn More"
    assert len(report["video_script_checks"]["recommended_checks"]) >= 3



def test_demo_api_has_basic_per_ip_rate_limit(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "_request_times", {})
    responses = [
        client.post("/api/compare", json={"creatives": [{"name": "A"}, {"name": "B"}]})
        for _ in range(main._RATE_LIMIT_PER_MINUTE + 1)
    ]
    assert responses[-1].status_code == 429
    assert responses[-1].headers["retry-after"] == "60"



def test_carousel_format_gets_sequence_specific_checklist():
    from app.main import format_specific_checks

    checks = format_specific_checks({"creative_type": "Carousel — Storytelling carousel"})
    assert "First card communicates a clear reason to swipe" in checks["review_points"]
    assert "Individual card images" in checks["missing_evidence"]


def test_catalog_format_discloses_missing_feed_evidence():
    from app.main import format_specific_checks

    checks = format_specific_checks({"creative_type": "Collection & Catalog — Product catalog ad"})
    assert "Catalog feed" in checks["missing_evidence"]
    assert any("Product set" in item for item in checks["review_points"])


def test_testimonial_format_flags_authenticity():
    from app.main import format_specific_checks

    checks = format_specific_checks({"creative_type": "Testimonial & Social Proof — Customer testimonial"})
    assert "Do not invent customers" in checks["integrity_warning"]


def test_static_image_does_not_claim_visual_inspection_without_provider():
    from app.main import format_specific_checks

    checks = format_specific_checks({"creative_type": "Static Image — Product hero shot"}, image_attached=True, image_inspected=False)
    assert "not visually inspected in local mode" in checks["visual"]


def _image_bytes(image_format="PNG", size=(2, 2)):
    buffer = io.BytesIO()
    Image.new("RGB", size, (120, 140, 160)).save(buffer, format=image_format)
    return buffer.getvalue()


def test_valid_png_upload_passes_image_validation(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image — Product hero shot"},
        files={"creative_file": ("sample.png", _image_bytes("PNG"), "image/png")},
    )
    assert response.status_code == 200
    assert response.json()["analysis_mode"] == "local_heuristic"
    assert "not visually inspected in local mode" in response.json()["format_specific_checks"]["visual"]


def test_valid_jpeg_upload_passes_image_validation(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image — Product hero shot"},
        files={"creative_file": ("sample.jpg", _image_bytes("JPEG"), "image/jpeg")},
    )
    assert response.status_code == 200


def test_header_only_fake_png_is_rejected():
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image"},
        files={"creative_file": ("fake.png", bytes.fromhex("89504E470D0A1A0A") + b"not-an-image", "image/png")},
    )
    assert response.status_code == 415
    assert "not a valid" in response.json()["detail"]


def test_image_pixel_limit_is_enforced(monkeypatch):
    from app import main

    monkeypatch.setattr(main, "MAX_IMAGE_PIXELS", 4)
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image"},
        files={"creative_file": ("sample.png", _image_bytes("PNG", (3, 3)), "image/png")},
    )
    assert response.status_code == 413
    assert "25-megapixel" in response.json()["detail"] or "dimensions exceed" in response.json()["detail"]


def test_image_upload_size_limit_is_enforced():
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Static Image"},
        files={"creative_file": ("large.png", b"x" * (8 * 1024 * 1024 + 1), "image/png")},
    )
    assert response.status_code == 413


def test_analysis_returns_industry_strategy_and_automated_plan(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = client.post(
        "/api/analyze",
        data={
            "industry": "Food delivery / restaurant",
            "creative_type": "Industry-specific — Food close-ups, food preparation, texture shots, and ASMR",
            "heading": "Fresh meals for lunch",
            "ad_copy": "Order our menu for your lunch break.",
            "offer": "Menu pricing as listed on page",
            "cta": "Order Now",
            "objective": "Sales",
            "destination": "",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["industry_strategy"]["key"] == "food_beverage"
    assert body["industry_strategy_recommendations"]["recommended_formats"]
    assert body["landing_page_review"]["status"] == "not_fetched"
    assert body["creative_variants"]
    assert body["test_plan"]
    assert body["risk_flags"]


def test_industry_detection_uses_explicit_industry():
    library = load_strategy_library()
    result = detect_industry({"industry": "Real estate", "ad_copy": ""}, {}, library)
    assert result["key"] == "real_estate"
    assert result["confidence"] in {"low", "medium", "high"}


def test_landing_page_fetch_rejects_http_and_local_urls():
    assert fetch_landing_page("http://127.0.0.1:8000")["status"] == "not_fetched"
    assert fetch_landing_page("https://localhost/admin")["status"] == "not_fetched"


def test_general_industry_fallback_when_evidence_is_missing():
    result = build_strategy_context({"creative_type": "Static Image", "heading": "", "ad_copy": "", "offer": "", "cta": "", "destination": ""})
    assert result["industry_strategy"]["key"] == "other"
    assert result["landing_page_review"]["status"] == "not_fetched"
