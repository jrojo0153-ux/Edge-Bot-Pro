import sys
from datetime import datetime
from pipeline import run_pipeline
from ml.model import audit_results
# Importa tu clase que conecta con la API (ejemplo: api_utils)
# from api_utils import OddsAPI 

if __name__ == "__main__":
    # Obtener hora actual en México
    # (Ajuste simple de UTC a CDMX)
    hora_actual = datetime.utcnow().hour - 6 
    if hora_actual < 0: hora_actual += 24

    if hora_actual == 22: # Si son las 10 PM
        print("🌙 Iniciando ciclo de auditoría nocturna...")
        # api = OddsAPI(key=os.getenv("API_KEY_ODDS"))
        # audit_results(api)
    else:
        print("🚀 Iniciando búsqueda de picks...")
        run_pipeline()
