import json

from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_reports_demo_mode_without_exposing_secret():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["telephony_connected"] is False
    assert data["synthetic_speech_enabled"] is False
    assert "api_key" not in data
    assert "NVIDIA_API_KEY" not in data


def test_menu_has_four_options():
    response = client.get("/api/menu")
    assert response.status_code == 200
    assert set(response.json()) == {"1", "2", "3", "4"}


def test_ivr_digit_returns_selected_option_and_audio_mapping():
    response = client.post("/api/ivr/digit", json={"digit": "3"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["digit"] == "3"
    assert data["audio_url"] == "/api/audio/option_3"
    assert len(data["choices"]) == 3
    assert data["choices"][0]["digit"] == "1"


def test_option_one_does_not_fake_or_substitute_a_recording():
    response = client.post("/api/ivr/digit", json={"digit": "1"})
    assert response.status_code == 200
    assert response.json()["audio_url"] is None
    assert response.json()["audio_available"] is False
    assert len(response.json()["choices"]) == 2


def test_invalid_ivr_digit_is_rejected_with_recording():
    response = client.post("/api/ivr/digit", json={"digit": "9"})
    assert response.status_code == 200
    assert response.json()["ok"] is False
    assert response.json()["audio_url"] == "/api/audio/invalid"


def test_audio_catalog_lists_only_prerecorded_assets():
    response = client.get("/api/audio")
    assert response.status_code == 200
    data = response.json()
    assert data["greeting"]["available"] is True
    assert data["option_2"]["available"] is True
    assert data["option_3"]["available"] is True
    assert data["option_4"]["available"] is True
    assert "option_1" not in data


def test_audio_endpoint_serves_wav():
    response = client.get("/api/audio/option_2")
    assert response.status_code == 200
    assert response.headers["content-type"] == "audio/wav"


def test_unknown_audio_event_is_not_served():
    response = client.get("/api/audio/not-a-real-event")
    assert response.status_code == 404


def test_chat_requires_nvidia_api_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "")
    response = client.post("/api/chat", json={"message": "नमस्कार"})
    assert response.status_code == 503
    assert "NVIDIA_API_KEY" in response.json()["detail"]



def test_ivr_sub_option_returns_guidance_without_audio():
    response = client.post("/api/ivr/digit", json={"digit": "3", "sub_option": "1"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["title"] == "पात्रता"
    assert "योजनेनुसार" in data["message"]
    assert data["audio_url"] is None


def test_invalid_sub_option_is_rejected():
    response = client.post("/api/ivr/digit", json={"digit": "2", "sub_option": "9"})
    assert response.status_code == 200
    assert response.json()["ok"] is False


def test_editable_system_prompt_file_is_loaded():
    prompt = main.load_system_prompt()
    assert "prototype" in prompt.lower()
    assert "Custom instructions" in prompt or "operator instructions" in prompt



def test_zero_returns_to_main_menu_with_recording():
    response = client.post("/api/ivr/digit", json={"digit": "0"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["digit"] == "0"
    assert data["audio_url"] == "/api/audio/main_menu"
    assert len(data["choices"]) == 4


def test_demo_check_reports_audio_and_never_claims_telephony():
    response = client.get("/api/demo-check")
    assert response.status_code == 200
    data = response.json()
    assert data["ready_for_browser_demo"] is True
    assert data["telephony_connected"] is False
    assert data["synthetic_speech_enabled"] is False
    assert data["option_1_recording_required"] is False
    assert data["missing_recordings"] == []


def test_each_menu_choice_has_expected_submenu_or_disclaimer():
    for digit in ("1", "2", "3"):
        response = client.post("/api/ivr/digit", json={"digit": digit})
        assert response.status_code == 200
        assert response.json()["choices"]
    response = client.post("/api/ivr/digit", json={"digit": "4"})
    assert response.status_code == 200
    assert response.json()["choices"] == []
    assert "हस्तांतरण होत नाही" in response.json()["message"]



def test_complaint_requires_configured_discord_webhook(monkeypatch):
    monkeypatch.setattr(main, "DISCORD_WEBHOOK_URL", "")
    response = client.post("/api/complaints", json={
        "category": "Other",
        "description": "A demo complaint description.",
        "privacy_confirmed": True,
    })
    assert response.status_code == 503


def test_complaint_requires_privacy_confirmation(monkeypatch):
    monkeypatch.setattr(main, "DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test/token")
    response = client.post("/api/complaints", json={
        "category": "Other",
        "description": "A demo complaint description.",
        "privacy_confirmed": False,
    })
    assert response.status_code == 400


def test_complaint_posts_only_minimal_fields_and_returns_menu_signal(monkeypatch):
    captured = {}

    class FakeResponse:
        status = 204
        def __enter__(self): return self
        def __exit__(self, *args): return False

    def fake_urlopen(request, timeout):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(main, "DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/test/token")
    monkeypatch.setattr(main, "urlopen", fake_urlopen)
    response = client.post("/api/complaints", json={
        "category": "Accessibility",
        "description": "The entrance ramp needs repair.",
        "privacy_confirmed": True,
    })
    assert response.status_code == 200
    assert response.json()["return_to_main_menu"] is True
    assert captured["body"]["embeds"][0]["fields"][0]["value"] == "Accessibility"
    assert len(captured["body"]["embeds"][0]["fields"]) == 2
    assert captured["timeout"] == 8
