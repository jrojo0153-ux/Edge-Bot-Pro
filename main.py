import os
import requests
# Sincronizamos con tus nombres de archivos reales
from data.odds_api import get_odds 
from ml.model import cargar_modelo, entrenar_modelo, predecir

# --- CONFIGURACIÓN SEGÚN TU REPORTE ---
EDGE_MINIMO = 0.08  # Nivel Conservador (8%)
CUOTA_MAXIMA = 10.0 # Recomendación técnica del reporte

def enviar_telegram(mensaje):
    token = os.getenv("API_KEY_TELEGRAM") # Asegúrate que este sea el nombre en tus Secrets
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
        except:
            pass

def main():
    print("🚀 SISTEMA EDGE PRO ACTIVADO")
    
    # 1. Cargar IA
    modelo = cargar_modelo() or entrenar_modelo()
    
    # 2. Obtener partidos (Usando tu archivo odds_api.py)
    partidos = get_odds()
    if not partidos:
        print("❌ No se pudieron obtener partidos.")
        return

    print(f"📊 Analizando {len(partidos)} eventos...")

    for p in partidos:
        try:
            # Adaptamos a la estructura de tu odds_api.py
            home_odds = p['odds'].get('home')
            away_odds = p['odds'].get('away')
            
            if not home_odds or home_odds > CUOTA_MAXIMA:
                continue

            # 3. Predicción
            if modelo:
                res = predecir(modelo, {"home_odds": home_odds, "away_odds": away_odds})
                prob_home = res['home'] if res else 0
            else:
                prob_home = 0.5

            edge = prob_home - (1/home_odds)
            
            # 4. Alerta de Valor
            if edge > EDGE_MINIMO:
                msg = (f"🎯 *ALERTA EDGE PRO*\n"
                       f"🏟️ {p['home']} vs {p['away']}\n"
                       f"📈 *Edge:* {round(edge*100, 2)}%\n"
                       f"💰 *Cuota:* {home_odds}")
                enviar_telegram(msg)
                print(f"✅ Alerta enviada para {p['home']}")

        except Exception as e:
            continue

if __name__ == "__main__":
    main()
