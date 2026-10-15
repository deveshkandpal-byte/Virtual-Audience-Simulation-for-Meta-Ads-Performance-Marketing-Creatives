from fastapi.testclient import TestClient

from app.main import app, heuristic_report

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


def test_video_upload_is_rejected_with_explanation():
    response = client.post(
        "/api/analyze",
        data={"creative_type": "Video", "objective": "Sales"},
        files={"creative_file": ("sample.mp4", b"not-a-real-video", "video/mp4")},
    )
    assert response.status_code == 415
    assert "Video upload is not supported" in response.json()["detail"]


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
