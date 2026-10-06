# AI Surveillance Crime Detection and Analysis

This project is a practical mini-project for an AI-based surveillance crime detection and alert system.

Features:
- live webcam or video stream processing
- YOLOv8 person detection
- restricted area monitoring
- loitering detection
- automated alert logging
- web dashboard for live monitoring
- buzzer-trigger simulation hook for hardware integration

## Project overview

The system watches a camera feed and detects suspicious activity such as:
- person entering a restricted zone
- suspicious loitering in a monitored area
- abnormal presence in a protected space

When an event is detected, the system logs the alert and can trigger an alarm or notification. The software is designed to be extended with actual hardware triggers like a buzzer, PIR sensor, or GSM module.

## Tech stack
- Python 3.10+
- OpenCV
- Ultralytics YOLOv8
- Flask
- NumPy

## Repository structure

```text
ai-crime-detection-surveillance/
├── app/
│   ├── __init__.py
│   ├── alert_manager.py
│   ├── config.py
│   ├── dashboard.py
│   ├── detection.py
│   └── video_source.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   └── index.html
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
└── run.sh
```

## Quick start

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python main.py --source 0
```

You can also use a recorded file:

```bash
python main.py --source sample_video.mp4
```

4. Open the dashboard in a browser:

```text
http://localhost:5000
```

## Default detection behavior

The software monitors a restricted region defined by a polygon on the frame.

If a detected person enters the region or stays there long enough, the app raises an alert such as:
- unauthorized intrusion
- loitering detected
- suspicious event in restricted area

## Alarm integration

The software currently logs alarm events in memory and writes them to `alerts.json`.

You can later connect this to:
- buzzer via Raspberry Pi GPIO
- SMS using Twilio
- email using SMTP
- Telegram bot
- external security dashboard

## Important note

The application uses `yolov8n.pt`, which will be downloaded automatically by Ultralytics the first time the model is loaded.

## Suggested project extension

For a final-year demo, you can add:
- face recognition
- restricted-zone setup from the dashboard
- database storage with SQLite/PostgreSQL
- SMS/Telegram alert notifications
- video recording for detected events
- Raspberry Pi hardware integration

## License

MIT
