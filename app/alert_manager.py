import os
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent
ALERTS_FILE = ROOT_DIR / "alerts.json"


@dataclass
class AlertEvent:
    alert_id: str
    alert_type: str
    message: str
    confidence: float
    timestamp: str
    image_path: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class AlertManager:
    def __init__(self, file_path: str = str(ALERTS_FILE)):
        self.file_path = Path(file_path)
        self.alerts: List[AlertEvent] = []
        self.load()

    def load(self):
        if self.file_path.exists():
            try:
                import json
                with open(self.file_path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                for item in data:
                    self.alerts.append(AlertEvent(**item))
            except Exception:
                self.alerts = []

    def save(self):
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        import json
        with open(self.file_path, "w", encoding="utf-8") as handle:
            json.dump([alert.to_dict() for alert in self.alerts], handle, indent=2)

    def add_alert(self, alert_type: str, message: str, confidence: float, image_path: Optional[str] = None):
        alert = AlertEvent(
            alert_id=f"{int(datetime.utcnow().timestamp() * 1000)}",
            alert_type=alert_type,
            message=message,
            confidence=confidence,
            timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            image_path=image_path,
        )
        self.alerts.insert(0, alert)
        self.alerts = self.alerts[:50]
        self.save()
        return alert

    def latest(self):
        return self.alerts[:10]
