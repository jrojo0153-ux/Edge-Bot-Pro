from data.odds_api import get_odds
from ml.model import load_or_train_model, predict_proba
from core.value import calculate_edge   # Crea este archivo si quieres
from core.parlay_builder import build_parlays
from core.telegram import send_telegram_message
from utils.logger import get_logger
from datetime import datetime

logger = get_logger()

def run_pipeline():
    logger.info("🚀 Iniciando Edge Bot Pro v2.0")
    
    model, scaler = load_or_train_model()
    matches = get_odds()
    
    if not matches:
        logger.warning("No se obtuvieron partidos")
        return
    
    picks = []
    
    for match in matches:
        probs = predict_proba(match, model, scaler)
        
        for outcome in ["home", "draw", "away"]:
            odd = match["odds"].get(outcome)
            if not odd:
                continue
                
            prob = probs[outcome]
            edge = prob - (1 / odd)
            
            if edge > 0.07:  # Umbral configurable
                picks.append({
                    "match": f"{match['home']} vs {match['away']}",
                    "pick": outcome,
                    "odds": odd,
                    "edge": edge,
                    "prob": prob
                })
    
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)[:15]
    
    if len(picks) < 2:
        logger.info("No hay suficientes picks con edge positivo")
        return
    
    parlays = build_parlays(picks)
    
    msg = f"🔥 **EDGE BOT PRO v2.0** - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    for p in parlays:
        msg += f"**{p['type']}** ({p['odds']}):\n"
        for leg in p["legs"]:
            msg += f"• {leg['match']} → {leg['pick']} @ {leg['odds']} (edge {leg['edge']:.3f})\n"
        msg += "\n"
    
    send_telegram_message(msg)
    logger.info(f"Enviado mensaje con {len(picks)} picks")
