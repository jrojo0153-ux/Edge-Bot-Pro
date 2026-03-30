import random

def predict_proba(event):
    """
    Retorna probabilidades para home, draw, away
    Siempre devuelve algo (aunque sea básico)
    """

    # Probabilidades base realistas
    home = random.uniform(0.35, 0.5)
    draw = random.uniform(0.2, 0.3)
    away = 1 - home - draw

    return {
        "home": round(home, 3),
        "draw": round(draw, 3),
        "away": round(away, 3)
    }
