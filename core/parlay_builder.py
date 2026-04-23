import logging

def build_parlays(picks):
    """
    Recibe una lista de picks con 'edge' y 'odds' calculados.
    Filtra cuotas exageradas y construye combinaciones lógicas.
    """
    if not picks:
        return []
    
    # 1. FILTRO DE CORDURA: 
    # Solo tomamos picks con cuotas entre 1.10 y 15.0 y con edge positivo.
    # Esto elimina automáticamente los errores de datos.
    picks_validos = [
        p for p in picks 
        if 1.10 <= p["odds"] <= 15.0 and p["edge"] > 0
    ]
    
    # Ordenamos por el mayor 'edge' (valor detectado por el modelo)
    picks_validos = sorted(picks_validos, key=lambda x: x["edge"], reverse=True)

    def create_parlay(name, size):
        # Si no hay suficientes picks de calidad, no creamos este parlay
        if len(picks_validos) < size:
            logging.warning(f"No hay suficientes picks válidos para parlay {name}")
            return None
            
        legs = picks_validos[:size]
        total_odds = 1.0
        for leg in legs:
            total_odds *= leg["odds"]
        
        # Límite máximo de cuota combinada para mantener el realismo (ej. 500.0)
        final_odds = round(total_odds, 2)
        if final_odds > 1000.0:
            final_odds = 1000.0
            
        return {
            "type": name,
            "legs": legs,
            "odds": final_odds
        }
    
    # Construcción de los 3 niveles de riesgo
    parlays = []
    
    # Conservador: 2 picks con más valor
    p1 = create_parlay("🛡️ Conservador", 2)
    if p1: parlays.append(p1)
    
    # Balanceado: 4 picks
    p2 = create_parlay("⚖️ Balanceado", 4)
    if p2: parlays.append(p2)
    
    # Agresivo: 6 picks
    p3 = create_parlay("💣 Agresivo", 6)
    if p3: parlays.append(p3)
    
    return parlays
