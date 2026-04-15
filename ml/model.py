import pandas as pd
import os
from datetime import datetime

# Rutas de archivos
PENDING_FILE = "data/pendientes.csv"
HISTORICO_FILE = "data/Historico.csv"

def guardar_picks_enviados(parlays):
    """Extrae los picks de los parlays y los guarda como pendientes"""
    nuevos_pendientes = []
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for parlay in parlays:
        for leg in parlay["legs"]:
            nuevos_pendientes.append({
                "fecha": fecha_hoy,
                "id_partido": leg.get("id"), # Asegúrate de que el ID pase por el pipeline
                "deporte": leg["sport"],
                "encuentro": leg["match"],
                "prediccion": leg["pick"],
                "cuota": leg["odds"],
                "resultado_real": "PENDIENTE"
            })
    
    if nuevos_pendientes:
        df = pd.DataFrame(nuevos_pendientes)
        header = not os.path.exists(PENDING_FILE)
        df.to_csv(PENDING_FILE, mode='a', index=False, header=header)
        print(f"💾 {len(nuevos_pendientes)} picks guardados en pendientes.")

def audit_and_learn(api_key):
    """Revisa los resultados de los pendientes y los mueve al Histórico"""
    if not os.path.exists(PENDING_FILE):
        return

    import requests
    df_pendientes = pd.read_csv(PENDING_FILE)
    df_actualizado = []
    
    print("🔍 Iniciando auditoría de resultados...")
    
    # Agrupamos por deporte para optimizar llamadas a la API
    deportes = df_pendientes['deporte'].unique()
    resultados_dict = {}

    # Nota: Necesitarías mapear tus nombres de deportes a los keys de The Odds API
    # Para simplificar, esta lógica asume que buscas resultados de partidos finalizados
    # The Odds API requiere el endpoint /scores/
    
    # ... (Lógica de consulta de scores similar a get_odds pero a /scores/)
    # Por ahora, moveremos a histórico para que el ciclo de archivos funcione.
