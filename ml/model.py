import pandas as pd
import numpy as np
import joblib
import os
from config import SPORTS

MODEL_DIR = "ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

# ==================== MODELO DUMMY (fuera de funciones) ====================
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
    
    # Guardamos el deporte para usarlo en predict_proba
    def __init__(self, sport):
        self.sport = sport

def get_model_path(sport):
    return f"{MODEL_DIR}/model_{sport}.pkl"

def load_or_train_model(sport):
    model_path = get_model_path(sport)
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            print(f"✅ Modelo cargado para {sport}")
            return model, None
        except:
            print(f"⚠️ Error cargando modelo, creando nuevo...")
    
    print(f"🔄 Creando modelo dummy para {sport}...")
    
    # Mostrar info del histórico
    try:
        df = pd.read_csv("data/Historico.csv")
        df.columns = df.columns.str.strip()
        print(f"✅ Histórico cargado: {len(df)} picks")
        print(f"   Deportes: {df['Deporte'].unique().tolist()}")
    except Exception as e:
        print(f"⚠️ No se pudo leer Historico.csv: {e}")
    
    # Crear y guardar el modelo
    model = SmartDummyModel(sport)
    joblib.dump(model, model_path)
    print(f"✅ Modelo dummy guardado para {sport}")
    
    return model, None

def predict_proba(match, model, scaler, sport):
    """Predicción usando el modelo dummy"""
    try:
        probs = model.predict_proba([[0]])[0]
    except:
        # Fallback seguro
        if SPORTS[sport]["has_draw"]:
            probs = [0.38, 0.28, 0.34]
        else:
            probs = [0.46, 0.00, 0.54]
    
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
