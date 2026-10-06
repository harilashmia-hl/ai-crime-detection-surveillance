import os
from pathlib import Path


def ensure_project_dirs():
    for directory in ["snapshots", "logs"]:
        Path(directory).mkdir(exist_ok=True)


if __name__ == "__main__":
    ensure_project_dirs()
    print("Project initialized.")
