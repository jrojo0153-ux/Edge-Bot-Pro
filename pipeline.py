from data.odds_api import get_odds
from ml.model import predict_proba
from ml.storage import save_results
from ml.update_results import update_results
from utils.telegram import send_telegram_message
from datetime import datetime


def run_pipeline():
    print("🚀 EDGE BOT PRO")

    update_results()

    matches = get_odds()

    picks = []

    for match in matches:
        probs = predict_proba(match)

        for outcome in ["home", "draw", "away"]:
            odd = match["odds"].get(outcome)

            if not odd:
                continue

            prob = probs[outcome]
            implied = 1 / odd
            edge = prob - implied

            picks.append({
                "match_id": match["id"],
                "match": f"{match['home']} vs {match['away']}",
                "pick": outcome,
                "odds": odd,
                "edge": edge
            })

    # ordenar por edge
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)

    # 1 pick por partido
    unique = []
    used = set()

    for p in picks:
        if p["match_id"] not in used:
            unique.append(p)
            used.add(p["match_id"])

    picks = unique[:10]

    if len(picks) < 3:
        print("❌ No picks suficientes")
        return

    conservador = picks[:2]
    balanceado = picks[:4]
    agresivo = picks[:6]

    def calc(parlay):
        total = 1
        for p in parlay:
            total *= p["odds"]
        return round(total, 2)

    def format_parlay(name, parlay):
        text = f"\n{name}:\n"
        for p in parlay:
            text += f"• {p['match']} → {p['pick']} ({p['odds']}, edge {round(p['edge'],3)})\n"
        text += f"💰 Cuota: {calc(parlay)}\n"
        return text

    msg = "🔥 EDGE BOT PRO\n"

    msg += format_parlay("🛡️ Conservador", conservador)
    msg += format_parlay("⚖️ Balanceado", balanceado)
    msg += format_parlay("💣 Agresivo", agresivo)

    print(msg)

    send_telegram_message(msg)

    save_results({
        "date": str(datetime.now()),
        "picks": picks
    })
