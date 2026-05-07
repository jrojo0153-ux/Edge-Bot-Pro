# data/odds_api.py - Módulo de conexión a The Odds API
import requests
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

from config import SPORTS, ENABLED_SPORTS

def get_odds() -> list:
    """
    Obtiene las cuotas de The Odds API para los deportes configurados
    
    Returns:
        list: Lista de partidos con sus cuotas
    """
    api_key = os.getenv("API_KEY_ODDS")
    
    if not api_key:
        logger.warning("⚠️ No API_KEY_ODDS encontrada en variables de entorno")
        return []

    all_matches = []

    for sport_code in ENABLED_SPORTS:
        if sport_code not in SPORTS:
            logger.warning(f"⚠️ Deporte {sport_code} no configurado en SPORTS")
            continue
        
        sport = SPORTS[sport_code]
        url = f"https://api.the-odds-api.com/v4/sports/{sport['key']}/odds/?apiKey={api_key}&regions=eu&markets=h2h&oddsFormat=decimal"
        
        try:
            res = requests.get(url, timeout=15)
            
            if res.status_code != 200:
                logger.error(f"❌ Error en {sport['name']}: {res.status_code}")
                if res.status_code == 429:
                    logger.error("⚠️ Límite de API alcanzado")
                continue
            
            data = res.json()
            logger.debug(f"📊 {sport['name']}: {len(data)} partidos de API")
            
            for game in data:
                try:
                    home = game["home_team"]
                    away = game["away_team"]
                    bookmakers = game.get("bookmakers", [])
                    
                    if not bookmakers:
                        logger.debug(f"⚠️ Sin bookmakers para {home} vs {away}")
                        continue

                    home_prices = []
                    away_prices = []
                    draw_prices = []

                    for bookie in bookmakers:
                        markets = bookie.get("markets", [])
                        if not markets:
                            continue
                        
                        outcomes = markets[0].get("outcomes", [])
                        for o in outcomes:
                            # Filtro de seguridad: ignorar cuotas individuales ridículas
                            if o["price"] > 50.0:
                                continue
                            
                            if o["name"] == home:
                                home_prices.append(o["price"])
                            elif o["name"] == away:
                                away_prices.append(o["price"])
                            else:
                                draw_prices.append(o["price"])

                    if not home_prices or not away_prices:
                        continue
                    
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
                    
                except KeyError as e:
                    logger.warning(f"⚠️ Error de clave en juego: {e}")
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Error procesando juego: {e}")
                    continue
                    
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout en {sport['name']}")
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de red en {sport['name']}: {e}")
        except Exception as e:
            logger.error(f"❌ Excepción en {sport['name']}: {e}")
    
    logger.info(f"✅ Obtenidos {len(all_matches)} partidos reales promediados")
    return all_matches
