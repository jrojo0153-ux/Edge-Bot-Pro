# core/parlay_builder.py - Constructor de Parlays
import logging
from config import PARLAY_SIZES

logger = logging.getLogger(__name__)

def calculate_parlay_odds(legs: list) -> float:
    """Calcula la cuota total de un parlay multiplicando las cuotas individuales"""
    odds = 1.0
    for leg in legs:
        odds *= leg["odds"]
    return round(odds, 2)

def build_parlays(picks: list, max_picks: int = 6) -> list:
    """
    Construye parlays de diferentes tamaños
    
    Args:
        picks: Lista de picks ordenados por edge
        max_picks: Tamaño máximo del parlay
    
    Returns:
        list: Lista de parlays construidos
    """
    parlays = []
    
    if len(picks) < 2:
        logger.warning("⚠️ No hay suficientes picks para construir parlays")
        return parlays
    
    # Construir parlays de diferentes tamaños
    for size_name, size in PARLAY_SIZES.items():
        if size > len(picks):
            continue
            
        legs = picks[:size]
        
        if not legs:
            continue
        
        parlay = {
            "type": size_name.capitalize(),
            "legs": legs,
            "odds": calculate_parlay_odds(legs),
            "avg_edge": round(sum(p["edge"] for p in legs) / len(legs), 3)
        }
        
        parlays.append(parlay)
        logger.info(f"✅ Parlay {size_name} creado: {size} legs, odds {parlay['odds']}")
    
    return parlays
