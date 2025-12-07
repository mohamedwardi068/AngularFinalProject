# storage.py
import json
import threading
from pathlib import Path

DATA_FILE = Path("data.json")
_lock = threading.Lock()

DEFAULT = {
    "users": [],       # {id, username, password_hash}
    "teams": [],       # {id, name, members: [user_id]}
    "predictions": []  # {id, user_id, team_id, fixture_key, competition, utcDate, home, away, predicted_home, predicted_away, created_at}
}

def _ensure():
    if not DATA_FILE.exists():
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(DEFAULT, f, indent=2)

def read_data():
    _ensure()
    with _lock:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)

def write_data(data):
    with _lock:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
