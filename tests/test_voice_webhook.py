import hashlib
import hmac
import json
from types import SimpleNamespace

from app.voice import routes as voice_routes
from tests.test_patient_api import patient_payload


def signed_request(client, body: dict, key: str):
    raw_body = json.dumps(body).encode()
    signature = hmac.new(key.encode(), raw_body, hashlib.sha256).hexdigest()
    return client.post(
        "/voice/register-patient",
        content=raw_body,
        headers={"Content-Type": "application/json", "X-Retell-Signature": signature},
    )


def test_rejects_invalid_signature(client, monkeypatch):
    monkeypatch.setattr(voice_routes, "get_settings", lambda: SimpleNamespace(retell_api_key="test-key"))
    response = client.post("/voice/register-patient", content=b"{}", headers={"X-Retell-Signature": "bad"})
    assert response.status_code == 401


def test_call_id_is_idempotent(client, monkeypatch):
    monkeypatch.setattr(voice_routes, "get_settings", lambda: SimpleNamespace(retell_api_key="test-key"))
    body = {"name": "register_patient", "call": {"call_id": "call-123"}, "args": patient_payload()}

    first = signed_request(client, body, "test-key")
    second = signed_request(client, body, "test-key")

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["patient"]["patient_id"] == second.json()["patient"]["patient_id"]
    assert second.json()["replayed"] is True
    assert len(client.get("/patients").json()["data"]) == 1
