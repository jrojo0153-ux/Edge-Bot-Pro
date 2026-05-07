# pipeline.py - Edge Bot Pro (Modo Odds API + ML)
import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pipeline.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Agregar raíz al path para imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar módulos
try:
    from data.odds_api import get_odds
    from ml.model import load_or_train_model, predict_proba
    from core.parlay_builder import build_parlays
    from core.telegram import send_telegram_message
    from config import SPORTS, ENABLED_SPORTS, PARLAY_SIZES
    logger.info("✅ Todos los módulos importados correctamente")
except ImportError as e:
    logger.error(f"❌ Error importando módulos: {e}")
    raise

def run_pipeline():
    """Ejecuta el pipeline completo de análisis"""
    logger.info("🚀 Iniciando Edge Bot Pro - Multi Deporte (Fútbol + NBA + MLB)")
    
    try:
        all_picks = []
        
        for sport_code in ENABLED_SPORTS:
            sport_config = SPORTS[sport_code]
            logger.info(f"📊 Procesando {sport_config['name']}...")
            
            try:
                model, scaler = load_or_train_model(sport_code)
                matches = [m for m in get_odds() if m["sport"] == sport_code]
                
                logger.info(f"📅 {len(matches)} partidos encontrados para {sport_config['name']}")
                
                picks = []
                for match in matches:
                    try:
                        probs = predict_proba(match, model, scaler, sport_code)
                        
                        for outcome in ["home", "away", "draw"]:
                            # Saltar draw si el deporte no lo tiene
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
                                    "prob": round(prob, 3),
                                    "id": match.get("id", "N/A")
                                })
                    except Exception as e:
                        logger.warning(f"⚠️ Error procesando match: {e}")
                        continue
                
                # Ordenar y limitar picks por deporte
                picks = sorted(picks, key=lambda x: x["edge"], reverse=True)[:10]
                all_picks.extend(picks)
                logger.info(f"✅ {sport_config['name']}: {len(picks)} picks con edge positivo")
                
            except Exception as e:
                logger.error(f"❌ Error procesando deporte {sport_code}: {e}")
                continue
        
        if len(all_picks) < 2:
            logger.info("⏹️ No hay suficientes picks en total (mínimo 2 requeridos)")
            return
        
        # Ordenar todos los picks por edge
        all_picks = sorted(all_picks, key=lambda x: x["edge"], reverse=True)
        
        # Construir parlays
        parlays = build_parlays(all_picks)
        
        # Construir mensaje
        msg = f"🔥 **EDGE BOT PRO - Multi Deporte** {datetime.now().strftime('%d/%m %H:%M')}\n\n"
        
        for parlay in parlays:
            msg += f"**{parlay['type']}** (Cuota ≈ {parlay['odds']})\n"
            for leg in parlay["legs"]:
                msg += f"• [{leg['sport']}] {leg['match']} → **{leg['pick']}** @ {leg['odds']} (edge {leg['edge']})\n"
            msg += "\n"
        
        msg += f"Total picks: {len(all_picks)}"
        
        # Enviar a Telegram
        success = send_telegram_message(msg)
        if success:
            logger.info("✅ Mensaje enviado a Telegram correctamente")
        else:
            logger.error("❌ Fallo al enviar a Telegram")
            
    except Exception as e:
        logger.error(f"❌ Error crítico en pipeline: {e}")
        raise

if __name__ == "__main__":
    run_pipeline()
