from data.odds_api import get_odds
from ml.model import load_or_train_model, predict_proba
from core.parlay_builder import build_parlays
from core.telegram import send_telegram_message
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("🚀 Iniciando Edge Bot Pro - Fútbol")
    
    model, scaler = load_or_train_model()
    matches = get_odds()
    
    if not matches:
        logger.warning("No se obtuvieron partidos de la API")
        return
    
    picks = []
    
    for match in matches:
        probs = predict_proba(match, model, scaler)
        
        for outcome in ["home", "draw", "away"]:
            odd = match["odds"].get(outcome)
            if not odd or odd < 1.01:
                continue
                
            prob = probs.get(outcome, 0.33)
            edge = prob - (1 / odd)
            
            if edge >= 0.07:   # Umbral mínimo
                picks.append({
                    "match": f"{match['home']} vs {match['away']}",
                    "pick": outcome.upper(),
                    "odds": odd,
                    "edge": round(edge, 3),
                    "prob": round(prob, 3)
                })
    
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)[:15]
    
    if len(picks) < 2:
        logger.info(f"Solo {len(picks)} picks con edge positivo. No se envía mensaje.")
        return
    
    parlays = build_parlays(picks)
    
    msg = f"🔥 **EDGE BOT PRO - Fútbol** {datetime.now().strftime('%d/%m %H:%M')}\n\n"
    
    for parlay in parlays:
        msg += f"**{parlay['type']}** (Cuota ≈ {parlay['odds']})\n"
        for leg in parlay["legs"]:
            msg += f"• {leg['match']} → **{leg['pick']}** @ {leg['odds']} (edge {leg['edge']})\n"
        msg += "\n"
    
    msg += f"Total picks encontrados: {len(picks)}"
    
    success = send_telegram_message(msg)
    if success:
        logger.info(f"Mensaje enviado correctamente con {len(picks)} picks")
    else:
        logger.error("Fallo al enviar mensaje a Telegram")
