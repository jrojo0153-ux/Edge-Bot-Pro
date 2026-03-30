import requests
import os

API_KEY = os.getenv("API_KEY_ODDS")

def get_odds():
    url = f"https://api.the-odds-api.com/v4/sports/upcoming/odds/?apiKey={API_KEY}&regions=eu&markets=h2h"

    res = requests.get(url)

    if res.status_code != 200:
        print("❌ Error odds:", res.text)
        return []

    data = res.json()
    matches = []

    for game in data:
        try:
            home = game["home_team"]
            away = game["away_team"]
            match_id = game["id"]

            outcomes = game["bookmakers"][0]["markets"][0]["outcomes"]

            odds = {}
            for o in outcomes:
                if o["name"] == home:
                    odds["home"] = o["price"]
                elif o["name"] == away:
                    odds["away"] = o["price"]
                else:
                    odds["draw"] = o["price"]

            matches.append({
                "id": match_id,
                "home": home,
                "away": away,
                "odds": odds
            })

        except:
            continue

    return matches
