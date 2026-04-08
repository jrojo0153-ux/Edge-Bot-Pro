import os
from data.live_matches import obtener_partidos
from ml.model import cargar_modelo, entrenar_modelo, predecir
from config import EDGE_MINIMO, BANKROLL_INICIAL
import requests

def enviar_telegram(msg):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        try:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        except:
            pass

def main():
    print("🚀 SISTEMA EDGE PRO: OPTIMIZANDO LIGAS")
    
    modelo = cargar_modelo() or entrenar_modelo()
    if not modelo:
        print("❌ Sin modelo.")
        return

    partidos = obtener_partidos()
    for partido in partidos:
        # 1. FILTRO DE CUOTAS ALTAS (Evita el 15% de efectividad en ligas menores)
        odds = partido.get('home_odds', 0)
        if odds > 12.0 or odds < 1.20:
            continue

        prob = predecir(modelo, partido)
        if prob:
            edge = prob - (1/odds)
            
            # 2. FILTRO DE EDGE CONSERVADOR
            # Subimos el requisito para Fútbol (si detectamos la liga)
            min_edge = 0.08 if "League" in partido.get('league', '') else EDGE_MINIMO
            
            if edge > min_edge:
                # 3. FILTRO DE LIGAS SUDAMERICANAS (Opcional si tienes el dato)
                # Exigimos más precisión aquí
                msg = (f"🎯 *ALERTA DE VALOR*\n"
                       f"⚽ {partido['home_team']} vs {partido['away_team']}\n"
                       f"📈 Edge: {round(edge*100, 2)}%\n"
                       f"💰 Cuota: {odds}")
                enviar_telegram(msg)

if __name__ == "__main__":
    main()
