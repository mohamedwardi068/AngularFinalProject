# predictions_logic.py
from datetime import datetime

def fixture_key(competition: str, fixture_obj: dict):
    """
    Create a stable key for a fixture. Uses id if present, else comp+utc+teams.
    fixture_obj is the match dictionary from the API
    """
    fid = fixture_obj.get("id") or fixture_obj.get("matchId") or None
    if fid:
        return f"{competition}:{fid}"
    # fallback:
    utc = fixture_obj.get("utcDate")
    home = fixture_obj.get("homeTeam", {}).get("name") or fixture_obj.get("homeTeam")
    away = fixture_obj.get("awayTeam", {}).get("name") or fixture_obj.get("awayTeam")
    return f"{competition}:{utc}:{home}:{away}"

def compute_prediction_points(pred_home: int, pred_away: int, real_home: int, real_away: int):
    """
    Scoring:
     - exact score: +5
     - correct winner/draw (but not exact): +3
     - otherwise 0
    """
    if real_home is None or real_away is None:
        return 0

    if pred_home == real_home and pred_away == real_away:
        return 5
    pred_diff = pred_home - pred_away
    real_diff = real_home - real_away
    if (pred_diff == 0 and real_diff == 0) or (pred_diff > 0 and real_diff > 0) or (pred_diff < 0 and real_diff < 0):
        return 3
    return 0

def iso_to_date(iso_str: str):
    if not iso_str:
        return None
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).date()
