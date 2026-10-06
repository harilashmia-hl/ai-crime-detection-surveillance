import argparse

from app.dashboard import create_dashboard_app


def parse_args():
    parser = argparse.ArgumentParser(description="AI Surveillance Crime Detection System")
    parser.add_argument("--source", type=str, default="0", help="Camera index or video file path")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host for the Flask app")
    parser.add_argument("--port", type=int, default=5000, help="Port for the Flask app")
    parser.add_argument("--model", type=str, default="yolov8n.pt", help="YOLO model path")
    parser.add_argument("--debug", action="store_true", help="Run Flask in debug mode")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    app = create_dashboard_app(source=args.source, model_path=args.model)
    app.run(host=args.host, port=args.port, debug=args.debug)
