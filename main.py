import sys
import os
from datetime import datetime, timezone, timedelta
from pipeline import run_pipeline
from ml.model import audit_and_learn

if __name__ == "__main__":
    # Solución al DeprecationWarning: Usamos timezone aware objects
    # UTC-6 para hora de México (CDMX)
    zona_horaria_mx = timezone(timedelta(hours=-6))
    ahora_mx = datetime.now(zona_horaria_mx)
    hora_mx = ahora_mx.hour
    
    print(f"🕒 Hora detectada en el bot: {ahora_mx.strftime('%H:%M')} (MX)")

    # A las 10 PM (22:00) corre la auditoría
    if hora_mx == 22:
        print("🌙 Hora de auditoría (10 PM MX). Verificando resultados del día...")
        api_key = os.getenv("API_KEY_ODDS")
        audit_and_learn(api_key)
    else:
        # En cualquier otro horario, busca picks
        print("🚀 Iniciando búsqueda de picks...")
        run_pipeline()
