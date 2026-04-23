from data.odds_api import get_odds
from ml.model import load_or_train_model, predict_proba
from core.parlay_builder import build_parlays
from core.telegram import send_telegram_message
from config import SPORTS, ENABLED_SPORTS, PARLAY_SIZES
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_pipeline():
    logger.info("🚀 Iniciando Edge Bot Pro - Multi Deporte (Fútbol + NBA + MLB)")
    
    all_picks = []
    
    for sport_code in ENABLED_SPORTS:
        sport_config = SPORTS[sport_code]
        logger.info(f"Procesando {sport_config['name']}...")
        
        model, scaler = load_or_train_model(sport_code)
        matches = [m for m in get_odds() if m["sport"] == sport_code]  # Filtrar por deporte
        
        picks = []
        for match in matches:
            probs = predict_proba(match, model, scaler, sport_code)
            
            for outcome in ["home", "away"]:   # draw solo si aplica
                if outcome == "draw" and not sport_config["has_draw"]:
                    continue
                    
                odd = match["odds"].get(outcome)
                if not odd or odd < 1.01:
                    continue
                    
                prob = probs.get(outcome, 0.5)
                edge = prob - (1 / odd)
                
                if edge >= sport_config["min_edge"]:
                    picks.append({
                        "sport": sport_config["name"],
                        "match": f"{match['home']} vs {match['away']}",
                        "pick": outcome.upper(),
                        "odds": odd,
                        "edge": round(edge, 3),
                        "prob": round(prob, 3)
                    })
        
        picks = sorted(picks, key=lambda x: x["edge"], reverse=True)[:10]
        all_picks.extend(picks)
        logger.info(f"{sport_config['name']}: {len(picks)} picks con edge positivo")
    
    if len(all_picks) < 2:
        logger.info("No hay suficientes picks en total")
        return
    
    # Ordenar todos los picks por edge
    all_picks = sorted(all_picks, key=lambda x: x["edge"], reverse=True)
    
    parlays = build_parlays(all_picks)
    
    msg = f"🔥 **EDGE BOT PRO - Multi Deporte** {datetime.now().strftime('%d/%m %H:%M')}\n\n"
    
    for parlay in parlays:
        msg += f"**{parlay['type']}** (Cuota ≈ {parlay['odds']})\n"
        for leg in parlay["legs"]:
            msg += f"• [{leg['sport']}] {leg['match']} → **{leg['pick']}** @ {leg['odds']} (edge {leg['edge']})\n"
        msg += "\n"
    
    msg += f"Total picks: {len(all_picks)}"
    
    success = send_telegram_message(msg)
    if success:
        logger.info("Mensaje enviado a Telegram correctamente")
    else:
        logger.error("Fallo al enviar a Telegram")
