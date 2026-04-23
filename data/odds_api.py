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
        if sport_code not in SPORTS: continue
        
        sport = SPORTS[sport_code]
        # Usamos decimales y región EU para mercados globales
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
                    bookmakers = game.get("bookmakers", [])
                    
                    if not bookmakers: continue

                    # Listas para calcular promedios y evitar errores de un solo bookie
                    home_prices = []
                    away_prices = []
                    draw_prices = []

                    for bookie in bookmakers:
                        markets = bookie.get("markets", [])
                        if not markets: continue
                        
                        outcomes = markets[0].get("outcomes", [])
                        for o in outcomes:
                            # Filtro de seguridad: ignorar cuotas individuales ridículas (> 50.0)
                            if o["price"] > 50.0: continue
                            
                            if o["name"] == home:
                                home_prices.append(o["price"])
                            elif o["name"] == away:
                                away_prices.append(o["price"])
                            else:
                                draw_prices.append(o["price"])

                    # Solo procedemos si tenemos datos de ambos equipos
                    if not home_prices or not away_prices: continue
                    
                    avg_odds = {
                        "home": round(sum(home_prices) / len(home_prices), 2),
                        "away": round(sum(away_prices) / len(away_prices), 2)
                    }
                    
                    if draw_prices:
                        avg_odds["draw"] = round(sum(draw_prices) / len(draw_prices), 2)

                    all_matches.append({
                        "id": game["id"],
                        "sport": sport_code,
                        "sport_name": sport["name"],
                        "home": home,
                        "away": away,
                        "odds": avg_odds,
                        "commence_time": game.get("commence_time")
                    })
                except Exception:
                    continue
        except Exception as e:
            print(f"❌ Excepción en {sport['name']}: {e}")
    
    print(f"✅ Obtenidos {len(all_matches)} partidos reales promediados")
    return all_matches
