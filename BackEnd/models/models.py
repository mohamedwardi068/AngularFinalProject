# models.py
from pydantic import BaseModel
from typing import Optional, List

class RegisterIn(BaseModel):
    username: str
    password: str

class LoginIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

class TeamCreate(BaseModel):
    name: str

class JoinTeamIn(BaseModel):
    team_id: int

class PredictionIn(BaseModel):
    competition: str
    fixture_id: Optional[int] = None  # if football-data provides id
    utcDate: str
    home: str
    away: str
    predicted_home: int
    predicted_away: int
