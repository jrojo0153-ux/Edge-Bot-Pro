import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def entrenar_modelo():
    ruta_csv = 'data/Historico.csv'
    
    # Verificamos si existe el archivo de tus resultados
    if not os.path.exists(ruta_csv):
        print(f"⚠️ {ruta_csv} no encontrado. El bot funcionará con lógica base.")
        return None
        
    try:
        df = pd.read_csv(ruta_csv)
        if df.empty: return None

        # Calculamos la diferencia de cuotas para detectar las 'bombas'
        df['diff'] = df['home_odds'] - df['away_odds']
        
        X = df[['home_odds', 'away_odds', 'diff']]
        y = df['resultado'] # 0:Local, 1:Empate, 2:Visitante
        
        # Entrenamos la IA con tus datos reales
        modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        modelo.fit(X, y)
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(modelo, 'models/modelo.pkl')
        print("✅ IA entrenada con tus resultados reales.")
        return modelo
    except Exception as e:
        print(f"❌ Error entrenamiento: {e}")
        return None

def cargar_modelo():
    ruta = 'models/modelo.pkl'
    if os.path.exists(ruta):
        try:
            return joblib.load(ruta)
        except:
            return None
    return None

def predecir(modelo, partido):
    try:
        h = float(partido['home_odds'])
        a = float(partido['away_odds'])
        # La IA predice basándose en lo que aprendió de tus fallos anteriores
        prob = modelo.predict_proba([[h, a, h-a]])[0]
        return {
            "home": round(float(prob[0]), 3),
            "draw": round(float(prob[1]), 3),
            "away": round(float(prob[2]), 3)
        }
    except:
        return None
