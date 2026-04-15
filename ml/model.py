import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from config import SPORTS

MODEL_DIR = "ml/models"
DATA_DIR = "data"
PENDING_PICKS = f"{DATA_DIR}/pendientes.csv"
HISTORICO_FILE = f"{DATA_DIR}/Historico.csv"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

class SmartDummyModel:
    def predict_proba(self, X):
        n = len(X)
        if SPORTS.get(self.sport, {}).get("has_draw", False):
            return np.array([[0.38, 0.28, 0.34]] * n)
        else:
            return np.array([[0.46, 0.00, 0.54]] * n)
    
    def __init__(self, sport):
        self.sport = sport

def guardar_pick_enviado(match_data):
    """Guarda el pick para ser auditado a las 10 PM"""
    df = pd.DataFrame([match_data])
    header = not os.path.exists(PENDING_PICKS)
    df.to_csv(PENDING_PICKS, mode='a', index=False, header=header)

def audit_results(api_connector):
    """Función para comparar resultados reales con los pendientes"""
    if not os.path.exists(PENDING_PICKS):
        print("No hay picks pendientes para auditar.")
        return

    df_pendientes = pd.read_csv(PENDING_PICKS)
    df_final = []

    for _, pick in df_pendientes.iterrows():
        # Aquí llamarías a tu API para obtener el resultado real
        resultado_real = api_connector.get_final_result(pick['id_partido'])
        
        if resultado_real:
            pick['resultado_final'] = resultado_real
            pick['acierto'] = 1 if resultado_real == pick['prediccion'] else 0
            df_final.append(pick)
    
    if df_final:
        df_historico = pd.DataFrame(df_final)
        header = not os.path.exists(HISTORICO_FILE)
        df_historico.to_csv(HISTORICO_FILE, mode='a', index=False, header=header)
        # Limpiar pendientes procesados
        os.remove(PENDING_PICKS)
        print(f"✅ Se auditaron {len(df_final)} partidos y se guardaron en el histórico.")

# --- Mantén tus funciones load_or_train_model y predict_proba iguales ---
