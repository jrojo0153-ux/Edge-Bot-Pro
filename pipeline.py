from ml.model import load_or_train_model, predict_proba, guardar_picks_enviados # Añadir import

def run_pipeline():
    # ... (todo tu código anterior igual hasta el envío de Telegram)
    
    success = send_telegram_message(msg)
    if success:
        logger.info("Mensaje enviado a Telegram correctamente")
        # GUARDAR PARA AUDITORÍA
        guardar_picks_enviados(parlays) 
    else:
        logger.error("Fallo al enviar a Telegram")
