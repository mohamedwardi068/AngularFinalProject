import requests

API_KEY = "1e83f2e3b20a4d779e7ef59f237a9436"   # << replace with your token
BASE_URL = "https://api.football-data.org/v4"

HEADERS = {
    "X-Auth-Token": API_KEY
}

def get_matches(competition_code, date_from=None, date_to=None):
    url = f"{BASE_URL}/competitions/{competition_code}/matches"
    params = {}
    if date_from and date_to:
        params["dateFrom"] = date_from
        params["dateTo"] = date_to
    
    resp = requests.get(url, headers=HEADERS, params=params)
    return resp.json()

def get_standings(competition_code):
    url = f"{BASE_URL}/competitions/{competition_code}/standings"
    resp = requests.get(url, headers=HEADERS)
    return resp.json()

# ---- LIST OF COMPETITIONS YOU NEED ---- #
TOP_5 = {
    "PL": "Premier League",
    "BL1": "Bundesliga",
    "SA": "Serie A",
    "PD": "La Liga",
    "FL1": "Ligue 1"
}

UCL = "CL"   # Champions League
