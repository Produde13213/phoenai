from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_health_reports_demo_mode_without_exposing_secret():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["telephony_connected"] is False
    assert "api_key" not in data
    assert "NVIDIA_API_KEY" not in data


def test_menu_has_four_options():
    response = client.get("/api/menu")
    assert response.status_code == 200
    assert set(response.json()) == {"1", "2", "3", "4"}


def test_ivr_digit_returns_selected_option():
    response = client.post("/api/ivr/digit", json={"digit": "3"})
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert response.json()["digit"] == "3"


def test_invalid_ivr_digit_is_rejected():
    response = client.post("/api/ivr/digit", json={"digit": "9"})
    assert response.status_code == 200
    assert response.json()["ok"] is False


def test_chat_requires_nvidia_api_key(monkeypatch):
    monkeypatch.setattr(main, "API_KEY", "")
    response = client.post("/api/chat", json={"message": "नमस्कार"})
    assert response.status_code == 503
    assert "NVIDIA_API_KEY" in response.json()["detail"]
