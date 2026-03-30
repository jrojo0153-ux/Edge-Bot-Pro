import requests

# =========================
# 🔐 CONFIG
# =========================
TELEGRAM_TOKEN = "8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE"
CHAT_ID = "8536626773"
OPENAI_API_KEY = "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"

# =========================
# ⚽ PARTIDOS
# =========================
def obtener_partidos():
    url = "https://www.thesportsdb.com/api/v1/json/3/livescore.php?s=Soccer"
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return []
        data = res.json()
        return data.get("events", []) if data else []
    except:
        return []

# =========================
# ⏱️ EXTRAER MINUTO
# =========================
def obtener_minuto(estado):
    try:
        if "'" in estado:
            return int(estado.replace("'", "").strip())
    except:
        return 0
    return 0

# =========================
# 🎯 FILTRO SNIPER DIOS
# =========================
def filtrar_partidos(partidos):
    filtrados = []

    for p in partidos:
        try:
            home = int(p.get("intHomeScore", 0))
            away = int(p.get("intAwayScore", 0))
            estado = p.get("strStatus", "")

            if "FT" in estado:
                continue

            minuto = obtener_minuto(estado)
            total = home + away

            # 🔴 OVER DIOS
            if 78 <= minuto <= 88 and home == away:
                p["tipo"] = "OVER SNIPER"
                p["minuto"] = minuto
                filtrados.append(p)

            # 🟢 UNDER DIOS
            elif minuto >= 75 and total <= 1:
                p["tipo"] = "UNDER SNIPER"
                p["minuto"] = minuto
                filtrados.append(p)

        except:
            continue

    return filtrados[:2]

# =========================
# 📊 EDGE DINÁMICO
# =========================
def calcular_apuesta(partido):
    tipo = partido.get("tipo")
    minuto = partido.get("minuto", 0)

    if tipo == "OVER SNIPER":
        prob = 0.60 + (minuto - 75) * 0.01  # sube con el tiempo
        cuota = 1.85

    elif tipo == "UNDER SNIPER":
        prob = 0.65 + (minuto - 70) * 0.005
        cuota = 1.65

    else:
        return None

    if prob > 0.80:
        prob = 0.80

    prob_casa = 1 / cuota
    edge = prob - prob_casa

    if edge <= 0:
        return None

    # 💰 Kelly fraccionado (más seguro)
    kelly = (prob * cuota - 1) / (cuota - 1)
    stake = kelly * 100 * 0.5  # 50% Kelly

    if stake > 40:
        stake = 40
    elif stake < 10:
        stake = 10

    return {
        "prob": round(prob, 2),
        "cuota": cuota,
        "edge": round(edge, 2),
        "stake": int(stake)
    }

# =========================
# 🧠 IA (OPCIONAL)
# =========================
def analizar_con_ia(partido):
    try:
        contexto = f"""
        Partido: {partido.get('strEvent')}
        Minuto: {partido.get('minuto')}
        Marcador: {partido.get('intHomeScore')} - {partido.get('intAwayScore')}
        Tipo: {partido.get('tipo')}

        Evalúa riesgo en una palabra (BAJO / MEDIO / ALTO)
        """

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": contexto}
            ]
        }

        res = requests.post(url, headers=headers, json=data)

        if res.status_code != 200:
            return "RIESGO: N/A"

        return res.json()["choices"][0]["message"]["content"]

    except:
        return "RIESGO: N/A"

# =========================
# 📲 TELEGRAM
# =========================
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# =========================
# 🚀 MAIN
# =========================
def main():
    partidos = obtener_partidos()

    if not partidos:
        return

    buenos = filtrar_partidos(partidos)

    if not buenos:
        return

    for partido in buenos:
        datos = calcular_apuesta(partido)

        if not datos:
            continue

        analisis = analizar_con_ia(partido)

        mensaje = f"""
🎯 SNIPER DIOS

{partido.get('strEvent')}
⏱️ Min {partido.get('minuto')}
⚽ {partido.get('intHomeScore')} - {partido.get('intAwayScore')}

🔥 {partido.get('tipo')}

📊 Prob: {datos['prob']*100}%
💰 Cuota: {datos['cuota']}
⚡ Edge: {datos['edge']}

💵 Stake: {datos['stake']}%

{analisis}
"""
        enviar_telegram(mensaje)

# =========================
# ▶️ RUN
# =========================
if __name__ == "__main__":
    main()
