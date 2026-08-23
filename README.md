# Solstice Kiosk

## 📌 Overview
A FastAPI‑based event check‑in kiosk with webhook integration and styled frontend.  
This project was built as part of the pivot deliverable to replace polling with asynchronous webhook flow.

## 🚀 Features
- FastAPI backend (`app.py`) with check‑in and webhook routes.
- JSON storage (`attendees.json`) for attendee state.
- Frontend (`index.html`) with JavaScript for check‑in and status updates.
- External CSS (`static/style.css`) for polished UI.
- Queue client (`queue_client.py`) and webhook handler (`webhook.py`) for async flow.

## 🛠 Setup
Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/WanjikuK60/Solstice-Kiosk.git
cd Solstice-Kiosk
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash
pip install fastapi uvicorn
