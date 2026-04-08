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
    
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        return joblib.load(model_path), joblib.load(scaler_path)
    
    # Entrenamiento básico (mejora agregando más datos por deporte)
    df = pd.read_csv("data/Historico.csv")  # Por ahora usa el mismo, luego separa por deporte
    
    # Features básicas
    df["odds_diff"] = df["home_odds"] - df["away_odds"]
    df["home_fav"] = df["home_odds"] < df["away_odds"]
    
    # Target simplificado (ajusta según tu CSV)
    df["target"] = 2  # placeholder - reemplaza con lógica real de resultado
    
    X = df[["home_odds", "away_odds", "odds_diff", "home_fav"]]
    y = df["target"]  # 0=away, 1=draw, 2=home
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(X_scaled, y)
    
    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    print(f"✅ Modelo entrenado para {sport}")
    return model, scaler

def predict_proba(match, model, scaler, sport):
    features = np.array([[
        match.get("odds", {}).get("home", 2.0),
        match.get("odds", {}).get("away", 2.0),
        match.get("odds", {}).get("home", 2.0) - match.get("odds", {}).get("away", 2.0),
        match.get("odds", {}).get("home", 2.0) < match.get("odds", {}).get("away", 2.0)
    ]])
    
    features_scaled = scaler.transform(features)
    probs = model.predict_proba(features_scaled)[0]
    
    has_draw = SPORTS[sport]["has_draw"]
    
    if has_draw:
        return {
            "home": round(probs[2], 3),
            "draw": round(probs[1], 3),
            "away": round(probs[0], 3)
        }
    else:
        # NBA y MLB no tienen empate → normalizamos home/away
        p_home = probs[2]
        p_away = probs[0]
        total = p_home + p_away
        return {
            "home": round(p_home / total, 3),
            "away": round(p_away / total, 3),
            "draw": 0.0
    }
