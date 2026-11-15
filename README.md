# Solstice Kiosk

An event check-in kiosk built with FastAPI. Check-in no longer waits on polling: the kiosk sends a badge print job, and the print vendor calls a webhook to confirm when the badge is printed.

## How it works

1. A guest enters their attendee ID at the kiosk. The browser calls `POST /checkin/{attendee_id}`.
2. The API publishes a print job to the vendor queue (`queue_client.py`) and answers `pending`.
3. When the badge is printed, the vendor calls `POST /webhook/print-status`.
4. On `success`, the attendee is marked as checked in. The kiosk page refreshes the attendee list every 3 seconds.

## API

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/` | Kiosk page |
| `GET` | `/attendees` | List attendees and their check-in state |
| `POST` | `/checkin/{attendee_id}` | Start check-in. Returns `pending` with a `job_id`, `already_checked_in`, or 404 |
| `POST` | `/webhook/print-status` | Vendor callback. Body: `{"attendee_id": "A001", "status": "success"}` (`success` or `failure`) |

## Run it

```bash
git clone https://github.com/WanjikuK60/Solstice-Kiosk.git
cd Solstice-Kiosk
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash; on macOS/Linux use: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

Open http://127.0.0.1:8000 and check in `A001`. To simulate the vendor confirming the print, run this in a second terminal:

```bash
curl -X POST http://127.0.0.1:8000/webhook/print-status \
  -H "Content-Type: application/json" \
  -d '{"attendee_id": "A001", "status": "success"}'
```

Within 3 seconds the kiosk shows A001 as checked in.

## Tests

```bash
pip install -r requirements-dev.txt
python -m pytest -q
```

The tests run against a temporary copy of the data, so `attendees.json` is never changed.

## Project structure

```
app.py            FastAPI routes and JSON storage
queue_client.py   Stand-in for the vendor print queue
index.html        Kiosk page
static/style.css  Styles
attendees.json    Sample attendee data
test_app.py       API tests
```

## Limits

Data is kept in a JSON file, which is fine for a demo but not for several kiosks at once; a real deployment would use a database. The webhook does not verify a signature yet. Production vendors sign their callbacks, and the API should reject unsigned ones.
