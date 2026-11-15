"""Solstice Kiosk: event check-in with an asynchronous badge-printing webhook.

Flow:
1. The kiosk calls POST /checkin/{attendee_id}.
2. The API publishes a print job to the vendor queue and answers "pending".
3. The print vendor later calls POST /webhook/print-status.
4. On success the attendee is marked as checked in.
"""

import json
from enum import Enum
from pathlib import Path
from threading import Lock

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from queue_client import publish_print_request

BASE_DIR = Path(__file__).resolve().parent
ATTENDEES_FILE = BASE_DIR / "attendees.json"

# One lock so two requests never write the JSON file at the same time.
_file_lock = Lock()

app = FastAPI(title="Solstice Kiosk")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


class PrintStatus(str, Enum):
    success = "success"
    failure = "failure"


class PrintStatusUpdate(BaseModel):
    attendee_id: str
    status: PrintStatus


def load_attendees() -> list[dict]:
    with ATTENDEES_FILE.open(encoding="utf-8") as file:
        return json.load(file)


def save_attendees(attendees: list[dict]) -> None:
    with ATTENDEES_FILE.open("w", encoding="utf-8") as file:
        json.dump(attendees, file, indent=2)
        file.write("\n")


def find_attendee(attendees: list[dict], attendee_id: str) -> dict:
    attendee = next((a for a in attendees if a["id"] == attendee_id), None)
    if attendee is None:
        raise HTTPException(status_code=404, detail="Attendee not found")
    return attendee


@app.get("/")
def read_root() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


@app.get("/attendees")
def list_attendees() -> list[dict]:
    with _file_lock:
        return load_attendees()


@app.post("/checkin/{attendee_id}")
def check_in(attendee_id: str) -> dict:
    with _file_lock:
        attendee = find_attendee(load_attendees(), attendee_id)

    if attendee["checked_in"]:
        return {"status": "already_checked_in"}

    job_id = publish_print_request(attendee_id)
    return {"status": "pending", "job_id": job_id}


@app.post("/webhook/print-status")
def print_status(update: PrintStatusUpdate) -> dict:
    with _file_lock:
        attendees = load_attendees()
        attendee = find_attendee(attendees, update.attendee_id)

        if update.status is PrintStatus.success and not attendee["checked_in"]:
            attendee["checked_in"] = True
            save_attendees(attendees)

    return {"message": "Status updated"}
