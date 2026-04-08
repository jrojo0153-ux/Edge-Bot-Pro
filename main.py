import os
import requests
# Ajustamos el import para que coincida con tu archivo en la carpeta data
try:
    from data.sofascore_api import obtener_partidos
except ImportError:
    # Si la función tiene otro nombre en tu archivo, cámbialo aquí
    def obtener_partidos(): return [] 

from ml.model import cargar_modelo, entrenar_modelo, predecir

# --- CONFIGURACIÓN NIVEL CONSERVADOR ---
EDGE_MINIMO = 0.08  # 8% de ventaja
CUOTA_MAXIMA = 10.0 # Filtro de seguridad para evitar 'bombas'

def enviar_telegram(mensaje):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, json={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}, timeout=10)
        except:
            print("❌ Error Telegram")

def main():
    print("🚀 SISTEMA EDGE PRO ACTIVADO")
    
    # 1. Cargar o entrenar modelo con tus resultados
    modelo = cargar_modelo() or entrenar_modelo()
    
    if not modelo:
        print("⚠️ No hay modelo entrenado. Usando lógica de respaldo.")

    # 2. Obtener partidos de SofaScore
    partidos = obtener_partidos()
    if not partidos:
        print("❌ No se recibieron partidos de SofaScore. Revisa data/sofascore_api.py")
        return

    print(f"📊 Analizando {len(partidos)} eventos...")

    for partido in partidos:
        try:
            odds = float(partido.get('home_odds', 0))
            
            # FILTRO DE SEGURIDAD: Evita las cuotas de 67 y 100 que bajan tu ROI
            if odds > CUOTA_MAXIMA or odds < 1.10:
                continue

            # 3. Predicción con la IA real
            if modelo:
                res = predecir(modelo, partido)
                prob_home = res['home'] if res else 0
            else:
                # Lógica básica si no hay modelo aún
                prob_home = 0.5 

            edge = prob_home - (1/odds)
            
            # 4. Alerta de Valor
            if edge > EDGE_MINIMO:
                msg = (f"🎯 *ALERTA EDGE PRO*\n"
                       f"🏟️ {partido['home_team']} vs {partido['away_team']}\n"
                       f"📈 *Edge:* {round(edge*100, 2)}%\n"
                       f"💰 *Cuota:* {odds}\n"
                       f"🤖 *IA Prob:* {round(prob_home*100, 1)}%")
                enviar_telegram(msg)
                print(f"✅ Alerta: {partido['home_team']}")

        except Exception as e:
            continue

    print("🏁 Proceso terminado.")

if __name__ == "__main__":
    main()
