import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os
from config import SPORTS

MODEL_DIR = "ml/models"
os.makedirs(MODEL_DIR, exist_ok=True)

def get_model_path(sport):
    return f"{MODEL_DIR}/model_{sport}.pkl"

def get_scaler_path(sport):
    return f"{MODEL_DIR}/scaler_{sport}.pkl"

def load_or_train_model(sport):
    model_path = get_model_path(sport)
    scaler_path = get_scaler_path(sport)
    
    # Si ya existe modelo entrenado, cargarlo
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        print(f"✅ Modelo cargado para {sport}")
        return joblib.load(model_path), joblib.load(scaler_path)
    
    print(f"🔄 Entrenando modelo para {sport}...")
    
    # Cargar datos históricos
    try:
        df = pd.read_csv("data/Historico.csv")
    except Exception as e:
        print(f"⚠️ No se pudo leer Historico.csv: {e}. Usando modelo dummy.")
        return create_dummy_model(sport)
    
    if len(df) < 5:
        print("⚠️ Muy pocos datos históricos. Usando modelo dummy.")
        return create_dummy_model(sport)
    
    # Features
    df["odds_diff"] = df["home_odds"] - df["away_odds"]
    df["home_fav"] = (df["home_odds"] < df["away_odds"]).astype(int)
    
    # Target: 0 = away win, 1 = draw, 2 = home win
    # Ajusta según cómo tengas la columna "resultado" en tu CSV
    if "resultado" in df.columns:
        df["target"] = df["resultado"].astype(int)
    else:
        # Si no tienes columna resultado, usa un placeholder (no ideal)
        df["target"] = 2
    
    # Verificar clases
    unique_classes = df["target"].unique()
    print(f"Clases encontradas en datos: {unique_classes}")
    
    if len(unique_classes) < 2:
        print("⚠️ Solo una clase en los datos históricos. Usando modelo dummy.")
        return create_dummy_model(sport)
    
    X = df[["home_odds", "away_odds", "odds_diff", "home_fav"]]
    y = df["target"]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Modelo más robusto
    model = LogisticRegression(
        max_iter=1000, 
        class_weight='balanced',   # Ayuda con desbalance
        solver='lbfgs'
    )
    model.fit(X_scaled, y)
    
    # Guardar
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    
    print(f"✅ Modelo entrenado correctamente para {sport} con {len(unique_classes)} clases")
    return model, scaler

def create_dummy_model(sport):
    """Modelo dummy que devuelve probabilidades fijas razonables"""
    # Creamos un modelo falso que siempre predice probabilidades típicas
    class DummyModel:
        def predict_proba(self, X):
            n = len(X)
            if SPORTS[sport]["has_draw"]:
                return np.array([[0.35, 0.30, 0.35]] * n)  # away, draw, home
            else:
                return np.array([[0.48, 0.0, 0.52]] * n)   # away, draw=0, home
    
    scaler = StandardScaler()  # scaler dummy
    print(f"✅ Usando modelo dummy (fallback) para {sport}")
    return DummyModel(), scaler

def predict_proba(match, model, scaler, sport):
    features = np.array([[
        match.get("odds", {}).get("home", 2.0),
        match.get("odds", {}).get("away", 2.0),
        match.get("odds", {}).get("home", 2.0) - match.get("odds", {}).get("away", 2.0),
        1 if match.get("odds", {}).get("home", 2.0) < match.get("odds", {}).get("away", 2.0) else 0
    ]])
    
    try:
        features_scaled = scaler.transform(features)
        probs = model.predict_proba(features_scaled)[0]
    except:
        # Si falla, usar probabilidades por defecto
        probs = [0.48, 0.04, 0.48] if not SPORTS[sport]["has_draw"] else [0.35, 0.30, 0.35]
    
    has_draw = SPORTS[sport]["has_draw"]
    
    if has_draw:
        return {"home": round(probs[2], 3), "draw": round(probs[1], 3), "away": round(probs[0], 3)}
    else:
        p_home = probs[2]
        p_away = probs[0]
        total = p_home + p_away + 1e-8
        return {
            "home": round(p_home / total, 3),
            "away": round(p_away / total, 3),
            "draw": 0.0
        }
