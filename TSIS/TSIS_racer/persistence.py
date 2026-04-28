import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
SETTINGS_FILE = BASE_DIR / "settings.json"
LEADERBOARD_FILE = BASE_DIR / "leaderboard.json"

DIFFICULTIES = ["Easy", "Normal", "Hard"]
CAR_COLORS = {
    "Blue": [0, 170, 255],
    "Green": [0, 200, 120],
    "Red": [230, 80, 80],
    "Yellow": [240, 200, 70],
}
DEFAULT_SETTINGS = {
    "sound": True,
    "car_color": "Blue",
    "difficulty": "Normal",
    "username": "Player",
}


def clean_name(name):
    text = "".join(ch for ch in str(name).strip() if ch.isalnum() or ch in " _-")[:12].strip()
    return text or "Player"


def _load(path, default):
    if not path.exists():
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default.copy() if isinstance(default, dict) else list(default)
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        path.write_text(json.dumps(default, indent=2), encoding="utf-8")
        return default.copy() if isinstance(default, dict) else list(default)


def _save(path, data):
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def _score_key(row):
    return (row["score"], row["distance"], row["coins"])


def _normalize_entry(item):
    return {
        "name": clean_name(item.get("name", "Player")),
        "score": int(item.get("score", 0)),
        "distance": int(item.get("distance", 0)),
        "coins": int(item.get("coins", 0)),
    }


def _unique_best_rows(rows):
    unique = {}
    for row in rows:
        current = unique.get(row["name"])
        if current is None or _score_key(row) >= _score_key(current):
            unique[row["name"]] = row
    board = list(unique.values())
    board.sort(key=_score_key, reverse=True)
    return board[:10]


def load_settings():
    data = _load(SETTINGS_FILE, DEFAULT_SETTINGS)
    settings = DEFAULT_SETTINGS.copy()
    if isinstance(data, dict):
        settings.update(data)
    if settings["difficulty"] not in DIFFICULTIES:
        settings["difficulty"] = "Normal"
    if settings["car_color"] not in CAR_COLORS:
        settings["car_color"] = "Blue"
    settings["sound"] = bool(settings["sound"])
    settings["username"] = clean_name(settings["username"])
    return settings


def save_settings(settings):
    data = {
        "sound": bool(settings.get("sound", True)),
        "car_color": settings.get("car_color", "Blue"),
        "difficulty": settings.get("difficulty", "Normal"),
        "username": clean_name(settings.get("username", "Player")),
    }
    _save(SETTINGS_FILE, data)
    return data


def load_leaderboard():
    board = _load(LEADERBOARD_FILE, [])
    if not isinstance(board, list):
        board = []
    clean = [_normalize_entry(item) for item in board if isinstance(item, dict)]
    clean = _unique_best_rows(clean)
    _save(LEADERBOARD_FILE, clean)
    return clean


def add_leaderboard_entry(entry):
    board = load_leaderboard()
    board.append(_normalize_entry(entry))
    board = _unique_best_rows(board)
    _save(LEADERBOARD_FILE, board)
    return board