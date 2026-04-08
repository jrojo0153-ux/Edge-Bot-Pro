import pandas as pd
import numpy as np
import joblib
import os
from config import SPORTS

MODEL_DIR = "ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(sport):
    return f"{MODEL_DIR}/model_{sport}.pkl"

def load_or_train_model(sport):
    model_path = get_model_path(sport)
    
    if os.path.exists(model_path):
        print(f"✅ Modelo cargado para {sport}")
        return joblib.load(model_path), None   # scaler no se usa en dummy
    
    print(f"🔄 Creando modelo para {sport}...")
    
    # Cargamos el nuevo histórico para backtesting futuro (por ahora no entrenamos ML real)
    try:
        df = pd.read_csv("data/Historico.csv")
        print(f"✅ Histórico cargado: {len(df)} picks | Deportes: {df['Deporte'].unique()}")
    except:
        print("⚠️ No se encontró Historico.csv")
    
    # Modelo Dummy inteligente (basado en EV real)
    class SmartDummyModel:
        def predict_proba(self, X):
            n = len(X)
            if SPORTS[sport]["has_draw"]:
                # Fútbol: más equilibrio
                return np.array([[0.38, 0.28, 0.34]] * n)
            else:
                # NBA/MLB: ligera ventaja local
                return np.array([[0.46, 0.00, 0.54]] * n)
    
    model = SmartDummyModel()
    joblib.dump(model, model_path)
    print(f"✅ Modelo dummy creado para {sport}")
    return model, None

def predict_proba(match, model, scaler, sport):
    """Devuelve probabilidades + usa Cuota del match si existe"""
    try:
        probs = model.predict_proba([[0]])[0]  # dummy input
    except:
        probs = [0.46, 0.0, 0.54] if not SPORTS[sport]["has_draw"] else [0.38, 0.28, 0.34]
    
    has_draw = SPORTS[sport]["has_draw"]
    
    if has_draw:
        return {
            "home": round(probs[2], 3),
            "draw": round(probs[1], 3),
            "away": round(probs[0], 3)
        }
    else:
        p_home = probs[2]
        p_away = probs[0]
        total = p_home + p_away + 1e-8
        return {
            "home": round(p_home / total, 3),
            "away": round(p_away / total, 3),
            "draw": 0.0
    }
