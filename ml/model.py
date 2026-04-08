from sklearn.linear_model import LogisticRegression
import numpy as np

# Datos de ejemplo: [fuerza_local, fuerza_visitante]
X_train = np.array([[10, 5], [5, 10], [8, 8], [2, 6]]) 
y_train = np.array(['home', 'away', 'draw', 'away']) # Resultados: 0=away, 1=draw, 2=home

model = LogisticRegression()
model.fit(X_train, y_train)

def predict_proba(match_stats):
    # match_stats: [fuerza_local, fuerza_visitante]
    probs = model.predict_proba([match_stats])[0]
    return {
        "away": round(probs[0], 3),
        "draw": round(probs[1], 3),
        "home": round(probs[2], 3)
    }

# predicción consistente: 
# print(predict_proba([9, 4])) 
