import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def entrenar_modelo():
    ruta_csv = 'data/Historico.csv'
    if not os.path.exists(ruta_csv):
        print("⚠️ Historico.csv no encontrado. Sube tus resultados para activar la IA.")
        return None
        
    try:
        df = pd.read_csv(ruta_csv)
        # Diferencia de cuotas para detectar las 'bombas' del reporte
        df['diff'] = df['home_odds'] - df['away_odds']
        
        X = df[['home_odds', 'away_odds', 'diff']]
        y = df['resultado'] # 0:Local, 1:Empate, 2:Visitante
        
        # Modelo balanceado para evitar el error de Accuracy 1.0 (Overfitting)
        modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        modelo.fit(X, y)
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(modelo, 'models/modelo.pkl')
        print("✅ IA entrenada con éxito.")
        return modelo
    except Exception as e:
        print(f"❌ Error entrenamiento: {e}")
        return None

def cargar_modelo():
    if os.path.exists('models/modelo.pkl'):
        return joblib.load('models/modelo.pkl')
    return None

def predecir(modelo, partido):
    try:
        h, a = float(partido['home_odds']), float(partido['away_odds'])
        prob = modelo.predict_proba([[h, a, h-a]])[0]
        return {"home": float(prob[0]), "draw": float(prob[1]), "away": float(prob[2])}
    except:
        return None
