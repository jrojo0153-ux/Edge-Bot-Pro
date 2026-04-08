import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import os

def entrenar_modelo():
    ruta_csv = 'data/Historico.csv'
    
    # Si no has subido el archivo, el bot te avisará
    if not os.path.exists(ruta_csv):
        print("⚠️ No se encontró Historico.csv. Sube el archivo de resultados.")
        return None
        
    try:
        df = pd.read_csv(ruta_csv)
        # Calculamos la diferencia de cuotas (donde el bot se confunde)
        df['diff'] = df['home_odds'] - df['away_odds']
        
        X = df[['home_odds', 'away_odds', 'diff']]
        y = df['resultado']
        
        # Modelo real: Aprende que cuotas altas = derrota del local
        modelo = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        modelo.fit(X, y)
        
        os.makedirs('models', exist_ok=True)
        joblib.dump(modelo, 'models/modelo.pkl')
        print("✅ IA entrenada con tus resultados reales.")
        return modelo
    except Exception as e:
        print(f"❌ Error al procesar resultados: {e}")
        return None
