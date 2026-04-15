import sys
import os
from datetime import datetime
from pipeline import run_pipeline
from ml.model import audit_and_learn

if __name__ == "__main__":
    # Obtener hora actual en CDMX (UTC-6)
    hora_mx = (datetime.utcnow().hour - 6) % 24
    
    # A las 10 PM (22:00) corre la auditoría
    if hora_mx == 22:
        print("🌙 Hora de auditoría (10 PM MX). Verificando resultados del día...")
        api_key = os.getenv("API_KEY_ODDS")
        audit_and_learn(api_key)
    else:
        # En cualquier otro horario, busca picks
        run_pipeline()
