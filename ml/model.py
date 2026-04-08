import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def entrenar_modelo():
    ruta_csv = 'data/Historico.csv'
    if not os.path.exists(ruta_csv):
        return None
        
    df = pd.read_csv(ruta_csv)
    
    # Ingeniería de Variables para detectar fallos en ligas
    df['diff'] = df['home_odds'] - df['away_odds']
    
    # Características: Cuotas + Diferencial + Identificador de Liga (si existe)
    features = ['home_odds', 'away_odds', 'diff']
    X = df[features]
    y = df['resultado'] # 0: Local, 1: Empate, 2: Visitante
    
    # Usamos un modelo más robusto para evitar el Overfitting (max_depth)
    modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    modelo.fit(X, y)
    
    os.makedirs('models', exist_ok=True)
    joblib.dump(modelo, 'models/modelo.pkl')
    return modelo

def predecir(modelo, partido):
    try:
        h = partido['home_odds']
        a = partido['away_odds']
        
        # EL FILTRO DE SEGURIDAD: 
        # Si la cuota es > 15.0, la probabilidad real suele ser mucho menor de lo que dice la IA
        if h > 15.0: return 0.05 
        
        # Predicción basada en el modelo entrenado
        prob = modelo.predict_proba([[h, a, h-a]])[0]
        # prob[0] es Local, prob[1] es Empate, prob[2] es Visitante
        return float(prob[0]) 
    except Exception as e:
        print(f"⚠️ Error en predicción: {e}")
        return None
