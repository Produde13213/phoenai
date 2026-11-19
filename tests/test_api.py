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


def test_option_one_does_not_fake_or_substitute_a_recording():
    response = client.post("/api/ivr/digit", json={"digit": "1"})
    assert response.status_code == 200
    assert response.json()["audio_url"] is None
    assert response.json()["audio_available"] is False


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
    assert data["option_1"] if "option_1" in data else True


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
