from datetime import date, timedelta

from app import main


def patient_payload(**overrides):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "02/14/1988",
        "sex": "Female",
        "phone_number": "(415) 555-2671",
        "email": "jane@example.com",
        "address_line_1": "10 Market Street",
        "city": "San Francisco",
        "state": "ca",
        "zip_code": "94105",
    }
    payload.update(overrides)
    return payload


def create_patient(client, **overrides):
    response = client.post("/patients", json=patient_payload(**overrides))
    assert response.status_code == 201, response.text
    return response.json()["data"]


def test_create_get_filter_update_and_soft_delete(client):
    created = create_patient(client)
    assert created["phone_number"] == "4155552671"
    assert created["state"] == "CA"
    assert created["date_of_birth"] == "1988-02-14"

    listed = client.get("/patients", params={"last_name": "Doe", "date_of_birth": "1988-02-14", "phone_number": "415-555-2671"})
    assert listed.status_code == 200
    assert [patient["patient_id"] for patient in listed.json()["data"]] == [created["patient_id"]]

    updated = client.put(f"/patients/{created['patient_id']}", json={"city": "Oakland", "preferred_language": "Spanish"})
    assert updated.status_code == 200
    assert updated.json()["data"]["city"] == "Oakland"
    assert updated.json()["data"]["preferred_language"] == "Spanish"

    deleted = client.delete(f"/patients/{created['patient_id']}")
    assert deleted.status_code == 200
    assert deleted.json()["data"]["deleted"] is True
    assert client.get(f"/patients/{created['patient_id']}").status_code == 404
    assert client.get("/patients").json()["data"] == []


def test_rejects_future_date_and_invalid_phone(client):
    future_date = (date.today() + timedelta(days=1)).isoformat()
    response = client.post("/patients", json=patient_payload(date_of_birth=future_date, phone_number="123"))
    assert response.status_code == 422
    body = response.json()
    assert body["data"] is None
    assert body["error"]["code"] == "validation_error"


def test_sqlite_record_persists_between_requests(client):
    created = create_patient(client)
    main.engine.dispose()
    retrieved = client.get(f"/patients/{created['patient_id']}")
    assert retrieved.status_code == 200
    assert retrieved.json()["data"]["patient_id"] == created["patient_id"]
