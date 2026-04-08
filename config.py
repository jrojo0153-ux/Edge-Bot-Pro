import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY_ODDS = os.getenv("API_KEY_ODDS")

# Configuración del bot
MIN_EDGE = 0.07          # 7% mínimo (ajustable)
MAX_STAKE_PERCENT = 35
MIN_STAKE = 8
MAX_PICKS_PARLAY = {"conservador": 2, "balanceado": 4, "agresivo": 6}
