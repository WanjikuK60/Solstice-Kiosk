from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.post("/webhook/print-status")
async def print_status(request: Request):
    data = await request.json()
    attendee_id = data["attendee_id"]
    status = data["status"]  # "success" or "failure"

    # Update attendee record
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
