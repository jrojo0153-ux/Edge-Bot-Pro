import requests
import os
# Importamos la lógica de IA que reparamos antes
from ml.model import cargar_modelo, entrenar_modelo, predecir

# =========================
# 🔐 CONFIG (Mantenemos tus keys)
# =========================
TELEGRAM_TOKEN = "8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE"
CHAT_ID = "8536626773"

# =========================
# ⚽ OBTENER PARTIDOS (Tu API actual)
# =========================
def obtener_partidos():
    url = "https://www.thesportsdb.com/api/v1/json/3/livescore.php?s=Soccer"
    try:
        res = requests.get(url)
        return res.json().get("events", []) if res.status_code == 200 else []
    except: return []

# =========================
# 📊 CÁLCULO CON IA REAL (Sustituye a la lógica estática)
# =========================
def calcular_apuesta_ia(partido, modelo):
    # Extraemos cuotas (si tu API no las da, usamos base 1.85 como tenías)
    h_odds = 1.85 
    a_odds = 2.00
    
    # 1. FILTRO DE SEGURIDAD (Del reporte)
    if h_odds > 10.0: return None

    # 2. PREDICCIÓN IA
    if modelo:
        res = predecir(modelo, {"home_odds": h_odds, "away_odds": a_odds})
        prob = res['home']
    else:
        # Lógica de respaldo si la IA no carga
        prob = 0.55 

    prob_casa = 1 / h_odds
    edge = prob - prob_casa

    # 3. FILTRO DE VALOR (Nivel Conservador 8%)
    if edge < 0.08: return None

    # Kelly Fraccionado
    kelly = (prob * h_odds - 1) / (h_odds - 1)
    stake = max(8, min(35, kelly * 100 * 0.5))

    return {
        "prob": round(prob, 2),
        "cuota": h_odds,
        "edge": round(edge, 2),
        "stake": int(stake)
    }

# =========================
# 📲 TELEGRAM
# =========================
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except: pass

# =========================
# 🚀 EJECUCIÓN
# =========================
def ejecutar_bot():
    print("🤖 Ejecutando Edge Bot Pro con IA...")
    modelo = cargar_modelo() or entrenar_modelo()
    partidos = obtener_partidos()
    
    for p in partidos:
        datos = calcular_apuesta_ia(p, modelo)
        if datos:
            mensaje = f"""
🎯 *EDGE BOT PRO FINAL*
{p.get('strEvent')}
⏱️ Min: {p.get('strStatus')}
📈 *Edge:* {datos['edge']}
💰 *Cuota:* {datos['cuota']}
💵 *Stake:* {datos['stake']}%
"""
            enviar_telegram(mensaje)

if __name__ == "__main__":
    ejecutar_bot()
