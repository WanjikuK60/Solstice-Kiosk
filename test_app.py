import json

import pytest
from fastapi.testclient import TestClient

import app as kiosk

client = TestClient(kiosk.app)


@pytest.fixture(autouse=True)
def attendees_file(tmp_path, monkeypatch):
    """Point the app at a fresh copy of the data so tests never touch attendees.json."""
    path = tmp_path / "attendees.json"
    path.write_text(json.dumps([
        {"id": "A001", "name": "Alice", "checked_in": False},
        {"id": "A002", "name": "Bob", "checked_in": True},
    ]))
    monkeypatch.setattr(kiosk, "ATTENDEES_FILE", path)
    return path


def test_list_attendees():
    response = client.get("/attendees")
    assert response.status_code == 200
    assert [a["id"] for a in response.json()] == ["A001", "A002"]


def test_check_in_returns_pending_with_job_id():
    response = client.post("/checkin/A001")
    assert response.status_code == 200
    assert response.json()["status"] == "pending"
    assert response.json()["job_id"]


def test_check_in_already_checked_in():
    response = client.post("/checkin/A002")
    assert response.json() == {"status": "already_checked_in"}


def test_check_in_unknown_attendee_is_404():
    assert client.post("/checkin/NOPE").status_code == 404


def test_successful_print_marks_attendee_checked_in(attendees_file):
    response = client.post("/webhook/print-status", json={"attendee_id": "A001", "status": "success"})
    assert response.status_code == 200
    saved = json.loads(attendees_file.read_text())
    assert saved[0]["checked_in"] is True


def test_failed_print_leaves_attendee_waiting(attendees_file):
    client.post("/webhook/print-status", json={"attendee_id": "A001", "status": "failure"})
    saved = json.loads(attendees_file.read_text())
    assert saved[0]["checked_in"] is False


def test_webhook_rejects_bad_payload():
    response = client.post("/webhook/print-status", json={"attendee_id": "A001", "status": "maybe"})
    assert response.status_code == 422


def test_webhook_unknown_attendee_is_404():
    response = client.post("/webhook/print-status", json={"attendee_id": "NOPE", "status": "success"})
    assert response.status_code == 404
