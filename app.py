from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import json

app = FastAPI()

# Mount the static folder so CSS/JS/images can be served
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/checkin/{attendee_id}")
def checkin(attendee_id: str):
    with open("attendees.json", "r") as f:
        attendees = json.load(f)

    attendee = next((a for a in attendees if a["id"] == attendee_id), None)

    if not attendee:
        return {"error": "Attendee not found"}

    if attendee["checked_in"]:
        return {"status": "Already checked in"}

    # Simulate publishing to queue
    return {"status": "Pending", "job_id": attendee_id + "-job"}

@app.post("/webhook/print-status")
async def print_status(request: Request):
    data = await request.json()
    attendee_id = data["attendee_id"]
    status = data["status"]

    with open("attendees.json", "r+") as f:
        attendees = json.load(f)
        for a in attendees:
            if a["id"] == attendee_id and not a["checked_in"]:
                if status == "success":
                    a["checked_in"] = True
        f.seek(0)
        json.dump(attendees, f, indent=2)
        f.truncate()

    return {"message": "Status updated"}
