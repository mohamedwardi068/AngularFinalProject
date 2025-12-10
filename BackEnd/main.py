# main.py
from fastapi import FastAPI, HTTPException, Depends, Header
from typing import Optional
from models import RegisterIn, LoginIn, UserOut, TeamCreate, JoinTeamIn, PredictionIn
from storage import read_data, write_data
from auth_utils import hash_password, verify_password, create_access_token, decode_token
from predictions_logic import fixture_key, compute_prediction_points, iso_to_date
from services.football_api import get_matches
from datetime import datetime, timedelta

app = FastAPI(title="Football Predictions API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- helpers ----------
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    if authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        token = authorization
    payload = decode_token(token)
    if not payload:
        return None
    return {"id": payload.get("id"), "username": payload.get("username")}

def _next_id(items):
    return max((i.get("id", 0) for i in items), default=0) + 1

# -------- Auth ----------
@app.post("/register", response_model=UserOut)
def register(payload: RegisterIn):
    data = read_data()
    if any(u["username"] == payload.username for u in data["users"]):
        raise HTTPException(400, "username already taken")
    salt = payload.username[::-1]  # simple salt: reversible but fine for demo
    phash = hash_password(payload.password, salt)
    user = {"id": _next_id(data["users"]), "username": payload.username, "password_hash": phash, "salt": salt}
    data["users"].append(user)
    write_data(data)
    return {"id": user["id"], "username": user["username"]}

@app.post("/login")
def login(payload: LoginIn):
    data = read_data()
    user = next((u for u in data["users"] if u["username"] == payload.username), None)
    if not user:
        raise HTTPException(401, "invalid credentials")
    if not verify_password(payload.password, user["salt"], user["password_hash"]):
        raise HTTPException(401, "invalid credentials")
    token = create_access_token({"id": user["id"], "username": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# -------- Teams ----------
@app.post("/teams/create")
def create_team(payload: TeamCreate, current=Depends(get_current_user)):
    if current is None:
        raise HTTPException(401, "Unauthorized")
    data = read_data()
    # Check if user is already in a team
    for t in data["teams"]:
        if current["id"] in t["members"]:
             raise HTTPException(400, "User is already in a team")

    tid = _next_id(data["teams"])
    team = {"id": tid, "name": payload.name, "members": [current["id"]]}
    data["teams"].append(team)
    write_data(data)
    return team

@app.post("/teams/join")
def join_team(payload: JoinTeamIn, current=Depends(get_current_user)):
    if current is None:
        raise HTTPException(401, "Unauthorized")
    data = read_data()
    
    # Check if user is already in a team
    for t in data["teams"]:
        if current["id"] in t["members"]:
             raise HTTPException(400, "User is already in a team")

    team = next((t for t in data["teams"] if t["id"] == payload.team_id), None)
    if not team:
        raise HTTPException(404, "team not found")
    if current["id"] in team["members"]:
        return {"msg": "already member"}
    team["members"].append(current["id"])
    write_data(data)
    return {"msg": "joined", "team": team}

@app.get("/teams")
def list_teams():
    data = read_data()
    # Enrich members with usernames
    res = []
    for t in data["teams"]:
        members_rich = []
        for uid in t["members"]:
             user = next((u for u in data["users"] if u["id"] == uid), None)
             if user:
                 members_rich.append({"id": uid, "username": user["username"]})
        res.append({"id": t["id"], "name": t["name"], "members": members_rich})
    return res

# -------- Matches ----------
@app.get("/matches/{comp_code}")
def matches(comp_code: str):
    # Filter: Today -> Today + 7 days
    today = datetime.now().date()
    date_to = (today + timedelta(days=7))
    
    # API requires YYYY-MM-DD
    d_from = today.isoformat()
    d_to = date_to.isoformat()

    # We could cache this or just proxy for now
    data = get_matches(comp_code, date_from=d_from, date_to=d_to)
    # data has "matches": [...]
    return data.get("matches", [])


# -------- Predictions ----------
@app.post("/predictions")
def add_prediction(payload: PredictionIn, current=Depends(get_current_user)):
    if current is None:
        raise HTTPException(401, "Unauthorized")
    data = read_data()
    # create fixture key
    fk = f"{payload.competition}:{payload.fixture_id}" if payload.fixture_id else f"{payload.competition}:{payload.utcDate}:{payload.home}:{payload.away}"
    pred = {
        "id": _next_id(data["predictions"]),
        "user_id": current["id"],
        "team_id": None,  # optional: if the user belongs to a team we could default; caller can send team id in extended model
        "fixture_key": fk,
        "competition": payload.competition,
        "utcDate": payload.utcDate,
        "home": payload.home,
        "away": payload.away,
        "predicted_home": payload.predicted_home,
        "predicted_away": payload.predicted_away,
        "created_at": datetime.utcnow().isoformat()
    }
    data["predictions"].append(pred)
    write_data(data)
    return pred

@app.get("/predictions/me")
def my_predictions(current=Depends(get_current_user)):
    if current is None:
        raise HTTPException(401, "Unauthorized")
    data = read_data()
    my = [p for p in data["predictions"] if p["user_id"] == current["id"]]
    return my

# -------- Leaderboard ----------
@app.get("/leaderboard")
def leaderboard():
    """
    Compute team leaderboard by aggregating predictions points for finished matches.
    If a user belongs to no team we add their points to "Individual" bucket.
    """
    data = read_data()
    # build user->team mapping (first team if multiple)
    user_to_team = {}
    for t in data["teams"]:
        for uid in t["members"]:
            if uid not in user_to_team:
                user_to_team[uid] = t["id"]

    # map fixture results by fixture_key by fetching recent results from football-data
    # We'll fetch matches for competitions present in predictions
    competitions = set(p["competition"] for p in data["predictions"])
    fixture_results = {}  # fixture_key -> (home_goals, away_goals, status)

    for comp in competitions:
        try:
            resp = get_matches(comp)
        except Exception as e:
            print(f"Error fetching matches for {comp}: {e}")
            import traceback
            traceback.print_exc()
            resp = {}
        matches = resp.get("matches", []) if isinstance(resp, dict) else []
        for m in matches:
            fk = None
            if m.get("id"):
                fk = f"{comp}:{m.get('id')}"
            else:
                fk = f"{comp}:{m.get('utcDate')}:{m.get('homeTeam', {}).get('name')}:{m.get('awayTeam', {}).get('name')}"
            # extract fulltime scores if present
            score = m.get("score", {}).get("fullTime", {})
            home = score.get("home")
            away = score.get("away")
            fixture_results[fk] = {"home": home, "away": away, "status": m.get("status")}

    # compute points per user
    user_points = {}
    for p in data["predictions"]:
        fk = p["fixture_key"]
        res = fixture_results.get(fk)
        if not res:
            # maybe prediction used idless key — try fallback matching by utcDate+teams
            # already built some keys similarly; skip if not found
            continue
        if res["status"] != "FINISHED":
            continue
        pts = compute_prediction_points(p["predicted_home"], p["predicted_away"], res["home"], res["away"])
        user_points[p["user_id"]] = user_points.get(p["user_id"], 0) + pts

    # aggregate per team
    team_points = {}
    # initialize teams
    for t in data["teams"]:
        team_points[t["id"]] = {"team_id": t["id"], "team_name": t["name"], "points": 0, "members": t["members"]}

    # individuals bucket
    individual_points = {}
    for uid, pts in user_points.items():
        tid = user_to_team.get(uid)
        if tid:
            team_points[tid]["points"] += pts
        else:
            individual_points[uid] = pts

    # produce leaderboard list
    leaderboard = list(team_points.values())
    # also include individuals as "Individual: username"
    for uid, pts in individual_points.items():
        user = next((u for u in data["users"] if u["id"] == uid), None)
        if user:
            leaderboard.append({"team_id": None, "team_name": f"Individual - {user['username']}", "points": pts, "members": [uid]})

    # sort desc
    leaderboard.sort(key=lambda x: x["points"], reverse=True)
    return {"leaderboard": leaderboard}
