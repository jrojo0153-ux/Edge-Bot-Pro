from data.sofascore_api import get_matches
from data.odds_api import get_odds
from core.value import calculate_edge
from core.parlay_builder import build_parlays
from utils.telegram import send_telegram_message

from ml.storage import save_picks
from ml.update_results import update_results


def run_pipeline():
    print("🚀 BOT PRO INICIADO")

    # 🧠 ML update
    update_results()

    matches = get_matches()
    odds_data = get_odds()

    picks = []
    used = set()

    for game in odds_data:
        try:
            home = game["home_team"]
            away = game["away_team"]

            match_id = f"{home}-{away}"
            if match_id in used:
                continue

            outcomes = game["bookmakers"][0]["markets"][0]["outcomes"]

            best = None
            best_edge = -999

            for o in outcomes:
                odd = o["price"]
                name = o["name"]

                if odd < 1.4 or odd > 4.0:
                    continue

                if name.lower() == "draw":
                    continue

                edge = calculate_edge(odd)

                if edge > best_edge:
                    best_edge = edge
                    best = {
                        "match": f"{home} vs {away}",
                        "pick": name,
                        "odds": odd,
                        "edge": edge
                    }

            if best:
                picks.append(best)
                used.add(match_id)

        except:
            continue

    if not picks:
        print("❌ No picks")
        return

    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)

    parlays = build_parlays(picks)

    save_picks(picks)

    message = "🔥 PARLAYS AUTOMÁTICOS (ML + SOFASCORE)\n\n"

    for p in parlays:
        message += f"{p['type']}:\n"
        for leg in p["legs"]:
            message += f"• {leg['match']} → {leg['pick']} ({leg['odds']})\n"
        message += f"💰 {p['odds']}\n\n"

    send_telegram_message(message)
