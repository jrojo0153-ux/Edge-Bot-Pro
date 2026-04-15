from data.odds_api import get_odds
from ml.model import load_or_train_model, predict_proba, guardar_picks_enviados 
from core.parlay_builder import build_parlays
from core.telegram import send_telegram_message  # <--- ESTA LÍNEA ES LA QUE FALTA
from config import SPORTS, ENABLED_SPORTS, PARLAY_SIZES
from datetime import datetime
import logging

# ... resto del código del pipeline ...

def run_pipeline():
    # ... (todo tu código anterior igual hasta el envío de Telegram)
    
    success = send_telegram_message(msg)
    if success:
        logger.info("Mensaje enviado a Telegram correctamente")
        # GUARDAR PARA AUDITORÍA
        guardar_picks_enviados(parlays) 
    else:
        logger.error("Fallo al enviar a Telegram")
