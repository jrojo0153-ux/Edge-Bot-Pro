import os
import requests
# Corregido: Importa desde tu archivo real de SofaScore
from data.sofascore_api import obtener_partidos 
from ml.model import cargar_modelo, entrenar_modelo, predecir

# Configuración básica (puedes mover esto a config.py si prefieres)
EDGE_MINIMO = 0.08  # 8% de ventaja (Nivel Conservador)
CUOTA_MAXIMA = 12.0 # Filtro para evitar 'bombas' suicidas

def enviar_telegram(mensaje):
    """Envía las alertas a Telegram de forma segura"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        payload = {"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")

def main():
    print("🚀 SISTEMA EDGE PRO ACTIVADO")
    
    # 1. Cargar o Entrenar Modelo
    modelo = cargar_modelo()
    if not modelo:
        print("📡 Entrenando modelo por primera vez...")
        modelo = entrenar_modelo()

    if not modelo:
        print("❌ Error Crítico: No se pudo inicializar la IA.")
        return

    # 2. Obtener Partidos desde SofaScore
    partidos = obtener_partidos()
    if not partidos:
        print("❌ No hay partidos procesables en SofaScore.")
        return

    print(f"📊 Analizando {len(partidos)} partidos...")

    for partido in partidos:
        try:
            odds = float(partido.get('home_odds', 0))
            
            # FILTRO DE SEGURIDAD: Evita cuotas de 67.0 o 100.0 que bajan tu ROI
            if odds > CUOTA_MAXIMA or odds < 1.10:
                continue

            # 3. Predicción de la IA
            res = predecir(modelo, partido)
            if res:
                prob_home = res['home']
                edge = prob_home - (1/odds)
                
                # 4. Filtro de Valor
                if edge > EDGE_MINIMO:
                    msg = (f"🎯 *ALERTA DE VALOR*\n"
                           f"🏟️ {partido['home_team']} vs {partido['away_team']}\n"
                           f"📈 *Edge:* {round(edge*100, 2)}%\n"
                           f"💰 *Cuota:* {odds}\n"
                           f"🤖 *Prob. IA:* {round(prob_home*100, 1)}%")
                    enviar_telegram(msg)
                    print(f"✅ Alerta enviada: {partido['home_team']}")

        except Exception as e:
            print(f"⚠️ Error procesando partido: {e}")
            continue

    print("🏁 Ciclo completado.")

if __name__ == "__main__":
    main()
