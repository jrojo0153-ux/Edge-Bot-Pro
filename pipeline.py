from datetime import datetime

from data.odds_api import get_odds
from telegram import send_telegram_message
from storage import save_results
from ml.model import predict_proba


def run_pipeline():
    print("🚀 EDGE BOT PRO RUNNING")

    odds_data = get_odds()

    print(f"💰 Eventos con odds: {len(odds_data)}")

    if not odds_data:
        print("❌ No odds disponibles")
        return

    picks = []

    # =========================
    # 🔥 CREAR MATCHES DESDE ODDS (SIN API FOOTBALL)
    # =========================
    for event in odds_data:

        home = event["home"]
        away = event["away"]
        match_id = event["id"]

        odds = event["odds"]

        # ML dummy / real
        probs = predict_proba(event)

        for outcome in ["home", "draw", "away"]:
            odd = odds.get(outcome)

            if not odd or odd <= 1:
                continue

            prob = probs.get(outcome, 0.33)

            implied = 1 / odd
            edge = prob - implied

            picks.append({
                "match_id": match_id,
                "match": f"{home} vs {away}",
                "selection": outcome,
                "odd": odd,
                "edge": edge
            })

    # =========================
    # 🔥 ORDENAR POR EDGE
    # =========================
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)

    # =========================
    # ⚠️ FALLBACK SI EDGE = 0
    # =========================
    if len(picks) == 0:
        print("⚠️ No edge → usando odds directos")

        for event in odds_data:
            for outcome in ["home", "draw", "away"]:
                odd = event["odds"].get(outcome)

                if odd:
                    picks.append({
                        "match_id": event["id"],
                        "match": f'{event["home"]} vs {event["away"]}',
                        "selection": outcome,
                        "odd": odd,
                        "edge": 0
                    })

    # =========================
    # 🔒 1 PICK POR PARTIDO
    # =========================
    unique = []
    used = set()

    for p in picks:
        if p["match_id"] not in used:
            unique.append(p)
            used.add(p["match_id"])

    picks = unique[:10]

    if len(picks) < 3:
        print("❌ No suficientes picks")
        return

    # =========================
    # 🧑‍🍳 PARLAYS
    # =========================
    conservador = picks[:2]
    balanceado = picks[:4]
    agresivo = picks[:6]

    def calc(parlay):
        total = 1
        for p in parlay:
            total *= p["odd"]
        return round(total, 2)

    def format_parlay(name, parlay):
        text = f"\n{name}:\n"
        for p in parlay:
            text += f"• {p['match']} → {p['selection']} (cuota {p['odd']}, edge {round(p['edge'],3)})\n"
        text += f"💰 Cuota total: {calc(parlay)}\n"
        return text

    msg = "🔥 EDGE BOT PRO (ODDS + ML)\n"

    msg += format_parlay("🛡️ Conservador", conservador)
    msg += format_parlay("⚖️ Balanceado", balanceado)
    msg += format_parlay("💣 Agresivo", agresivo)

    print(msg)

    # =========================
    # 📲 TELEGRAM
    # =========================
    send_telegram_message(msg)

    # =========================
    # 💾 GUARDAR
    # =========================
    save_results({
        "date": str(datetime.now()),
        "picks": picks
    })

    print("✅ DONE")
