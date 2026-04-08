def build_parlays(picks):
    if not picks:
        return []
    
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)
    
    def create_parlay(name, size):
        legs = picks[:size]
        total_odds = 1.0
        for leg in legs:
            total_odds *= leg["odds"]
        
        return {
            "type": name,
            "legs": legs,
            "odds": round(total_odds, 2)
        }
    
    return [
        create_parlay("🛡️ Conservador", 2),
        create_parlay("⚖️ Balanceado", 4),
        create_parlay("💣 Agresivo", 6)
    ]
