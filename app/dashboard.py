import threading
from typing import Any

from flask import Flask, jsonify, render_template, Response

from app.alert_manager import AlertManager
from app.detection import SurveillanceDetector


class DashboardController:
    def __init__(self, source: str, model_path: str):
        self.app = Flask(__name__)
        self.alert_manager = AlertManager()
        self.detector = SurveillanceDetector(source=source, model_path=model_path)
        self._setup_routes()
        self._thread = None

    def _setup_routes(self):
        @self.app.route("/")
        def index():
            return render_template("index.html")

        @self.app.route("/video_feed")
        def video_feed():
            return Response(self._generate_video_feed(), mimetype="multipart/x-mixed-replace; boundary=frame")

        @self.app.route("/api/alerts")
        def api_alerts():
            return jsonify({"alerts": [alert.to_dict() for alert in self.alert_manager.latest()]})

        @self.app.route("/api/status")
        def api_status():
            return jsonify({
                "status": "running",
                "alert_count": len(self.alert_manager.alerts),
                "last_alert": self.alert_manager.alerts[0].to_dict() if self.alert_manager.alerts else None,
            })

    def _generate_video_feed(self):
        self.detector.open()
        while True:
            frame = self.detector.get_frame()
            if frame is None:
                continue
            processed = self.detector.process_frame(frame)
            if processed is None:
                continue
            encoded, buffer = cv2.imencode(".jpg", processed)
            if not encoded:
                continue
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")

    def run(self, host: str = "127.0.0.1", port: int = 5000, debug: bool = False):
        self.app.run(host=host, port=port, debug=debug)


def create_dashboard_app(source: str = "0", model_path: str = "yolov8n.pt") -> Flask:
    controller = DashboardController(source, model_path)
    return controller.app
