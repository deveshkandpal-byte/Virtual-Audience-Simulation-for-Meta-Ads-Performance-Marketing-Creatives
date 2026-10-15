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
