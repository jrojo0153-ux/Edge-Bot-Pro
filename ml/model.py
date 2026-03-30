import random

def predict_proba(match):
    home = random.uniform(0.4, 0.6)
    draw = random.uniform(0.2, 0.3)
    away = 1 - home - draw

    return {
        "home": round(home, 3),
        "draw": round(draw, 3),
        "away": round(away, 3)
    }
