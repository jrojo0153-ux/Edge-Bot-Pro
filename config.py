import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_KEY_ODDS = os.getenv("API_KEY_ODDS")

# ==================== CONFIGURACIÓN MULTI-DEPORTE ====================
SPORTS = {
    "soccer": {
        "key": "soccer",           # o "soccer_epl,soccer_laliga,soccer_champions_league" para ligas específicas
        "name": "Fútbol",
        "min_edge": 0.07,
        "has_draw": True
    },
    "nba": {
        "key": "basketball_nba",
        "name": "NBA",
        "min_edge": 0.06,          # NBA suele tener menos edge en moneyline
        "has_draw": False
    },
    "mlb": {
        "key": "baseball_mlb",
        "name": "MLB",
        "min_edge": 0.05,          # MLB tiene mucha varianza por pitching
        "has_draw": False
    }
}

# Opciones globales
MAX_PICKS_PER_SPORT = 10
PARLAY_SIZES = {
    "conservador": 2,
    "balanceado": 4,
    "agresivo": 6
}

ENABLED_SPORTS = ["soccer", "nba", "mlb"]   # Cambia aquí para activar/desactivar
