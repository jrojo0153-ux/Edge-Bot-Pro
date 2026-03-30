from data.odds_api import get_odds
from data.sofascore_api import get_team_rating
from core.value import calculate_edge
from core.parlay_builder import build_parlays
from utils.telegram import send_telegram_message

from ml.storage import save_picks
from ml.update_results import update_results


def run_pipeline():
    print("🔥 EDGE BOT PRO RUNNING")

    update_results()

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

            home_rating = get_team_rating(home)
            away_rating = get_team_rating(away)

            for o in outcomes:
                odd = o["price"]
                name = o["name"]

                if odd < 1.4 or odd > 4.0:
                    continue

                if name.lower() == "draw":
                    continue

                rating = home_rating if name == home else away_rating

                edge = calculate_edge(odd, rating)

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

    parlays = build_parlays(picks)

    save_picks(picks)

    msg = "🔥 EDGE BOT PRO PARLAYS\n\n"

    for p in parlays:
        msg += f"{p['type']}:\n"
        for leg in p["legs"]:
            msg += f"• {leg['match']} → {leg['pick']} ({leg['odds']})\n"
        msg += f"💰 {p['odds']}\n\n"

    print(msg)
    send_telegram_message(msg)
