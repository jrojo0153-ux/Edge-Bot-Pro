from data.odds_api import get_odds
from ml.model import load_or_train_model, predict_proba, guardar_picks_enviados 
from core.parlay_builder import build_parlays
from core.telegram import send_telegram_message  # <--- ESTA LÃNEA ES LA QUE FALTA
from config import SPORTS, ENABLED_SPORTS, PARLAY_SIZES
from datetime import datetime
import logging

# ... resto del cÃ³digo del pipeline ...

def run_pipeline():
    # 1. Obtener los datos (esto ya lo debes tener arriba)
    # odds = get_odds(...)
    # parlays = build_parlays(...)

    # 2. CONSTRUIR EL MENSAJE (Lo que faltaba)
    if not parlays:
        logging.info("No hay parlays para enviar hoy.")
        return

    # Aquí creamos la variable 'msg'
    msg = "🚀 **Nuevos Picks Detectados** 🚀\n\n"
    for p in parlays:
        msg += f"🔹 {p}\n" # Ajusta esto según cómo sea el objeto parlay

    # 3. ENVIAR EL MENSAJE
    # Ahora 'msg' ya existe y no dará error
    success = send_telegram_message(msg)
    
    if success:
        logging.info("Mensaje enviado a Telegram correctamente")
        guardar_picks_enviados(parlays) 
    else:
        logging.error("Fallo al enviar a Telegram")

