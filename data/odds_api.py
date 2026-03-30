import os
import requests

API_KEY = os.getenv("44dd2a172a7f8f0a2d6e0ab9a5534dad")

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
