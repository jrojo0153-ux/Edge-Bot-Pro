import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def entrenar_modelo():
    """Entrena la IA usando los resultados reales del Historico.csv"""
    ruta_csv = 'data/Historico.csv'
    
    # Verificación de seguridad para evitar errores en GitHub Actions
    if not os.path.exists(ruta_csv):
        print(f"⚠️ Archivo {ruta_csv} no encontrado. Por favor, créalo para activar la IA.")
        return None
        
    try:
        df = pd.read_csv(ruta_csv)
        if df.empty:
            return None

        # Ingeniería de variables: La diferencia de cuotas ayuda a detectar 'bombas'
        df['diff'] = df['home_odds'] - df['away_odds']
        
        # Variables de entrenamiento
        X = df[['home_odds', 'away_odds', 'diff']]
        y = df['resultado'] # 0:Local, 1:Empate, 2:Visitante
        
        # Modelo RandomForest: El más balanceado para deportes
        modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        modelo.fit(X, y)
        
        # Guardar modelo para uso futuro
        os.makedirs('models', exist_ok=True)
        joblib.dump(modelo, 'models/modelo.pkl')
        print("✅ IA entrenada correctamente con datos históricos.")
        return modelo
    except Exception as e:
        print(f"❌ Error en el entrenamiento: {e}")
        return None

def cargar_modelo():
    """Intenta cargar un modelo previamente entrenado"""
    ruta = 'models/modelo.pkl'
    if os.path.exists(ruta):
        try:
            return joblib.load(ruta)
        except:
            return None
    return None

def predecir(modelo, partido):
    """Calcula la probabilidad real basada en el aprendizaje del modelo"""
    try:
        h = float(partido['home_odds'])
        a = float(partido['away_odds'])
        
        # El modelo predice basándose en las cuotas actuales y su diferencia
        prob = modelo.predict_proba([[h, a, h-a]])[0]
        
        return {
            "home": round(float(prob[0]), 3),
            "draw": round(float(prob[1]), 3),
            "away": round(float(prob[2]), 3)
        }
    except Exception as e:
        print(f"⚠️ Error al predecir: {e}")
        return None
