import pandas as pd
import numpy as np
import joblib
import os
from datetime import datetime
from config import SPORTS

MODEL_DIR = "ml/models"
DATA_DIR = "data"
PENDING_FILE = "data/pendientes.csv"
HISTORICO_FILE = "data/Historico.csv"

# Crear carpetas si no existen
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ==================== CLASE Y FUNCIONES ORIGINALES ====================

class SmartDummyModel:
    """Modelo simple que no depende de entrenamiento pesado"""
    def predict_proba(self, X):
        n = len(X)
        if SPORTS.get(self.sport, {}).get("has_draw", False):
            # Fútbol: away, draw, home
            return np.array([[0.38, 0.28, 0.34]] * n)
        else:
            # NBA / MLB: away, draw=0, home
            return np.array([[0.46, 0.00, 0.54]] * n)
    
    def __init__(self, sport):
        self.sport = sport

def get_model_path(sport):
    return f"{MODEL_DIR}/model_{sport}.pkl"

def load_or_train_model(sport):
    """Carga el modelo existente o crea uno nuevo si falla"""
    model_path = get_model_path(sport)
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            print(f"✅ Modelo cargado para {sport}")
            return model, None
        except:
            print(f"⚠️ Error cargando modelo, creando nuevo...")
    
    print(f"🔄 Creando modelo dummy para {sport}...")
    model = SmartDummyModel(sport)
    joblib.dump(model, model_path)
    return model, None

def predict_proba(match, model, scaler, sport):
    """Predicción usando el modelo dummy"""
    try:
        probs = model.predict_proba([[0]])[0]
    except:
        if SPORTS[sport]["has_draw"]:
            probs = [0.38, 0.28, 0.34]
        else:
            probs = [0.46, 0.00, 0.54]
    
    has_draw = SPORTS[sport]["has_draw"]
    if has_draw:
        return {"home": round(probs[2], 3), "draw": round(probs[1], 3), "away": round(probs[0], 3)}
    else:
        p_home, p_away = probs[2], probs[0]
        total = p_home + p_away + 1e-8
        return {"home": round(p_home / total, 3), "away": round(p_away / total, 3), "draw": 0.0}

# ==================== NUEVAS FUNCIONES DE AUDITORÍA ====================

def guardar_picks_enviados(parlays):
    """Guarda los picks enviados en pendientes.csv"""
    nuevos_pendientes = []
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for parlay in parlays:
        for leg in parlay["legs"]:
            nuevos_pendientes.append({
                "fecha": fecha_hoy,
                "id_partido": leg.get("id", "N/A"),
                "deporte": leg["sport"],
                "encuentro": leg["match"],
                "prediccion": leg["pick"],
                "cuota": leg["odds"],
                "resultado_real": "PENDIENTE"
            })
    
    if nuevos_pendientes:
        df = pd.DataFrame(nuevos_pendientes)
        header = not os.path.exists(PENDING_FILE)
        df.to_csv(PENDING_FILE, mode='a', index=False, header=header)
        print(f"💾 {len(nuevos_pendientes)} picks guardados para auditoría.")

def audit_and_learn(api_key):
    """Mueve los pendientes al histórico (Simulación de aprendizaje)"""
    if not os.path.exists(PENDING_FILE):
        print("No hay picks pendientes.")
        return

    df_pendientes = pd.read_csv(PENDING_FILE)
    # Aquí irá la lógica de consulta a /scores en el futuro
    # Por ahora, simplemente los movemos al histórico para validar el ciclo
    header = not os.path.exists(HISTORICO_FILE)
    df_pendientes.to_csv(HISTORICO_FILE, mode='a', index=False, header=header)
    
    os.remove(PENDING_FILE)
    print("✅ Auditoría completada: Picks movidos al histórico.")
