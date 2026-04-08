import requests
import os

def get_odds():
    api_key = os.getenv("API_KEY_ODDS")
    if not api_key:
        print("⚠️ No API_KEY_ODDS encontrada")
        return []
    
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
    
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            print(f"❌ Error Odds API: {res.status_code} - {res.text[:200]}")
            return []
        
        data = res.json()
        matches = []
        
        for game in data:
            try:
                home = game["home_team"]
                away = game["away_team"]
                outcomes = game["bookmakers"][0]["markets"][0]["outcomes"] if game.get("bookmakers") else []
                
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
                    matches.append({
                        "id": game["id"],
                        "home": home,
                        "away": away,
                        "odds": odds,
                        "commence_time": game.get("commence_time")
                    })
            except:
                continue
        return matches
    except Exception as e:
        print(f"❌ Excepción en Odds API: {e}")
        return []
