import requests
import os
from config import SPORTS, ENABLED_SPORTS

def get_odds():
    api_key = os.getenv("API_KEY_ODDS")
    if not api_key:
        print("⚠️ No API_KEY_ODDS encontrada")
        return []

    all_matches = []

    for sport_code in ENABLED_SPORTS:
        sport = SPORTS[sport_code]
        url = f"https://api.the-odds-api.com/v4/sports/{sport['key']}/odds/?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
        
        try:
            res = requests.get(url, timeout=15)
            if res.status_code != 200:
                print(f"❌ Error en {sport['name']}: {res.status_code}")
                continue
            
            data = res.json()
            for game in data:
                try:
                    home = game["home_team"]
                    away = game["away_team"]
                    outcomes = game.get("bookmakers", [{}])[0].get("markets", [{}])[0].get("outcomes", [])
                    
                    odds = {}
                    for o in outcomes:
                        name = o["name"]
                        if name == home:
                            odds["home"] = o["price"]
                        elif name == away:
                            odds["away"] = o["price"]
                        else:
                            odds["draw"] = o.get("price")
                    
                    if odds.get("home") and odds.get("away"):
                        all_matches.append({
                            "id": game["id"],
                            "sport": sport_code,
                            "sport_name": sport["name"],
                            "home": home,
                            "away": away,
                            "odds": odds,
                            "commence_time": game.get("commence_time")
                        })
                except:
                    continue
        except Exception as e:
            print(f"❌ Excepción en {sport['name']}: {e}")
    
    print(f"✅ Obtenidos {len(all_matches)} partidos de {len(ENABLED_SPORTS)} deportes")
    return all_matches
