import requests

# 🔐 CONFIG
TELEGRAM_TOKEN = "8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE"
CHAT_ID = "8536626773"
OPENAI_API_KEY = "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"

# ⚽ Obtener partidos en vivo
def obtener_partidos():
    url = "https://www.thesportsdb.com/api/v2/json/3/livescore/soccer"
    res = requests.get(url).json()
    return res.get("events", [])

# 🧠 FILTROS PRO (AQUI ESTA EL DINERO)
def filtrar_partidos(partidos):
    filtrados = []

    for p in partidos:
        try:
            home = int(p.get("intHomeScore", 0))
            away = int(p.get("intAwayScore", 0))
            estado = p.get("strStatus", "")

            # SOLO partidos en juego
            if "FT" in estado:
                continue

            total_goles = home + away

            # 🎯 FILTRO CLAVE
            if total_goles <= 2:
                filtrados.append(p)

        except:
            continue

    return filtrados[:3]  # máximo 3 para no gastar mucho

# 🧠 ANALISIS IA
def analizar_con_ia(partido):
    contexto = f"""
    Analiza este partido en vivo como apostador profesional:

    Partido: {partido['strEvent']}
    Marcador: {partido['intHomeScore']} - {partido['intAwayScore']}
    Estado: {partido['strStatus']}

    Detecta:
    - Si es partido lento o abierto
    - Mejor apuesta (UNDER / OVER / NO APOSTAR)
    - Explicación corta

    Responde en formato claro para Telegram.
    """

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Eres un experto en apuestas deportivas en vivo especializado en detectar edge."},
            {"role": "user", "content": contexto}
        ]
    }

    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

# 📲 TELEGRAM
def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

# 🚀 MAIN
def main():
    partidos = obtener_partidos()
    buenos = filtrar_partidos(partidos)

    for partido in buenos:
        analisis = analizar_con_ia(partido)

        mensaje = f"""
🔥 ALERTA EDGE

{partido['strEvent']}
{partido['intHomeScore']} - {partido['intAwayScore']}

{analisis}
"""
        enviar_telegram(mensaje)

if __name__ == "__main__":
    main()
