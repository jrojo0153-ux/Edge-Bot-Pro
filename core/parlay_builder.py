def build_parlays(picks):
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)

    def create(name, size):
        legs = picks[:size]
        odds = 1
        for l in legs:
            odds *= l["odds"]

        return {
            "type": name,
            "legs": legs,
            "odds": round(odds, 2)
        }

    return [
        create("🛡️ Conservador", 2),
        create("⚖️ Balanceado", 4),
        create("💣 Agresivo", 6)
    ]
