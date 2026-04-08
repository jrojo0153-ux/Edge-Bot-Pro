import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
import os

MODEL_PATH = "ml/model.pkl"
SCALER_PATH = "ml/scaler.pkl"

def load_or_train_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
        model = joblib.load(MODEL_PATH)
        scaler = joblib.load(SCALER_PATH)
        print("✅ Modelo cargado")
        return model, scaler
    
    # Entrenamiento con datos históricos
    df = pd.read_csv("data/Historico.csv")
    # Features simples pero reales (puedes expandir mucho más)
    df["home_fav"] = df["home_odds"] < df["away_odds"]
    df["odds_diff"] = df["home_odds"] - df["away_odds"]
    
    # Target: 0=away win, 1=draw, 2=home win (simplificado)
    df["target"] = np.where(df["resultado"] == 1, 2, 
                   np.where(df["resultado"] == 0, 0, 1))  # Ajusta según tu CSV
    
    X = df[["home_odds", "away_odds", "odds_diff", "home_fav"]]
    y = df["target"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = LogisticRegression(max_iter=1000, class_weight='balanced')
    model.fit(X_train_scaled, y_train)
    
    # Guardar
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    
    print(f"✅ Modelo entrenado. Accuracy aproximada: {model.score(X_train_scaled, y_train):.2f}")
    return model, scaler

def predict_proba(match, model, scaler):
    # match debe tener home_odds y away_odds
    features = np.array([[match.get("home_odds", 2.0), 
                          match.get("away_odds", 2.0),
                          match.get("home_odds", 2.0) - match.get("away_odds", 2.0),
                          match.get("home_odds", 2.0) < match.get("away_odds", 2.0)]])
    
    features_scaled = scaler.transform(features)
    probs = model.predict_proba(features_scaled)[0]
    
    return {
        "home": round(probs[2], 3),   # Ajusta índices según tu target
        "draw": round(probs[1], 3),
        "away": round(probs[0], 3)
    }
