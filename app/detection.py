import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import cv2
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

from app.alert_manager import AlertManager


class SurveillanceDetector:
    def __init__(self, source: str = "0", model_path: str = "yolov8n.pt"):
        self.source = source
        self.model_path = model_path
        self.model = None
        self.capture = None
        self.alert_manager = AlertManager()
        self.last_alert_time = 0.0
        self.last_alert_type = None
        self.alert_cooldown = 10.0
        self.person_loiter_times: Dict[str, float] = {}
        self.armed = True

        self.resolution = (640, 480)
        self.roi_points = np.array([
            [int(0.15 * self.resolution[0]), int(0.65 * self.resolution[1])],
            [int(0.85 * self.resolution[0]), int(0.65 * self.resolution[1])],
            [int(0.85 * self.resolution[0]), int(0.95 * self.resolution[1])],
            [int(0.15 * self.resolution[0]), int(0.95 * self.resolution[1])],
        ], dtype=np.int32)

    def open(self):
        self.capture = cv2.VideoCapture(int(self.source) if self.source.isdigit() else self.source)
        if not self.capture.isOpened():
            raise RuntimeError(f"Unable to open video source: {self.source}")
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        if YOLO is not None:
            self.model = YOLO(self.model_path)

    def get_frame(self):
        if self.capture is None:
            self.open()
        success, frame = self.capture.read()
        if not success:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.capture.read()
            if not success:
                return None
        return frame

    def point_in_polygon(self, point, polygon):
        x, y = point
        inside = False
        n = len(polygon)
        for i in range(n):
            j = (i + 1) % n
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
            if intersect:
                inside = not inside
        return inside

    def _get_person_boxes(self, frame):
        if self.model is None:
            return []
        try:
            results = self.model(frame, imgsz=640, conf=0.35, verbose=False)
        except Exception:
            return []

        detections = []
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                cls_name = result.names.get(cls_id, "unknown")
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                if cls_name.lower() == "person":
                    detections.append({
                        "bbox": (x1, y1, x2, y2),
                        "confidence": confidence,
                        "center": ((x1 + x2) / 2, (y1 + y2) / 2),
                    })
        return detections

    def _trigger_alert(self, frame, alert_type: str, message: str, confidence: float):
        now = time.time()
        if self.last_alert_type == alert_type and (now - self.last_alert_time) < self.alert_cooldown:
            return frame

        self.last_alert_time = now
        self.last_alert_type = alert_type
        snapshot_path = self._save_snapshot(frame)
        self.alert_manager.add_alert(alert_type, message, confidence, snapshot_path)
        return frame

    def _save_snapshot(self, frame):
        snapshot_dir = Path("snapshots")
        snapshot_dir.mkdir(exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"alert_{timestamp}.jpg"
        path = snapshot_dir / file_name
        cv2.imwrite(str(path), frame)
        return str(path)

    def process_frame(self, frame):
        if frame is None:
            return None

        display = frame.copy()

        if self.model is None:
            cv2.polylines(display, [self.roi_points], isClosed=True, color=(0, 255, 255), thickness=2)
            cv2.putText(display, "Model not loaded", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            return display

        detections = self._get_person_boxes(frame)
        if not detections:
            cv2.polylines(display, [self.roi_points], isClosed=True, color=(0, 255, 255), thickness=2)
            cv2.putText(display, "No person detected", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            return display

        for detection in detections:
            x1, y1, x2, y2 = detection["bbox"]
            center = detection["center"]
            cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.circle(display, (int(center[0]), int(center[1])), 4, (0, 0, 255), -1)

            if self.point_in_polygon(center, self.roi_points):
                person_key = f"{int(center[0])}:{int(center[1])}"
                self.person_loiter_times.setdefault(person_key, time.time())
                elapsed = time.time() - self.person_loiter_times[person_key]

                if elapsed >= 5:
                    cv2.putText(display, "LOITERING ALERT", (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    display = self._trigger_alert(
                        display,
                        "loitering",
                        f"Person stayed in restricted area for {elapsed:.1f} seconds",
                        detection["confidence"],
                    )
                else:
                    cv2.putText(display, "Inside restricted area", (x1, max(0, y1 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                    display = self._trigger_alert(
                        display,
                        "unauthorized_entry",
                        "Person entered restricted zone",
                        detection["confidence"],
                    )
            else:
                for key in list(self.person_loiter_times.keys()):
                    if key.startswith(f"{int(center[0])}:") and abs(int(center[1]) - int(float(key.split(":")[1]))) < 30:
                        self.person_loiter_times.pop(key, None)

        cv2.polylines(display, [self.roi_points], isClosed=True, color=(0, 255, 255), thickness=2)
        cv2.putText(display, "Restricted Zone", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        return display
