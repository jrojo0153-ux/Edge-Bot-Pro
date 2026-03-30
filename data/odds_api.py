import os
import requests

API_KEY = os.getenv("API_KEY_ODDS")

def get_odds():
    url = "https://api.the-odds-api.com/v4/sports/soccer/odds/"

    params = {
        "apiKey": API_KEY,
        "regions": "eu",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }

    try:
        res = requests.get(url, params=params)

        if res.status_code != 200:
            return []

        return res.json()

    except:
        return []
