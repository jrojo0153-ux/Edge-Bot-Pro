from ml.model import get_winrate

def calculate_edge(odds, rating=0.5):
    prob_ml = get_winrate()

    # 🔥 combinar ML + SofaScore
    prob = (prob_ml * 0.7) + (rating * 0.3)

    implied = 1 / odds

    return prob - implied
