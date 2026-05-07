# core/telegram.py - Módulo de envío a Telegram
import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

# Configurar logging
logger = logging.getLogger(__name__)

def send_telegram_message(message: str) -> bool:
    """
    Envía un mensaje a Telegram
    
    Args:
        message: Mensaje a enviar (soporta Markdown)
    
    Returns:
        bool: True si se envió correctamente, False otherwise
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    # Validar credenciales
    if not token or not chat_id:
        logger.error("⚠️ Telegram credentials no configuradas")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        response = requests.post(
            url, 
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }, 
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("✅ Mensaje enviado a Telegram")
            return True
        else:
            logger.error(f"❌ Error Telegram {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout enviando a Telegram")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de red: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return False
