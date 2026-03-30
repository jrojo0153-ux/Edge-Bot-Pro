import requests

# =========================
# 🔐 CONFIGURA TUS DATOS
# =========================
TELEGRAM_TOKEN = "8679602699:AAHNDRLLbEFzojJDYozkZYLoS08xmXQEHn0"
CHAT_ID = "8536626773"
OPENAI_API_KEY = "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"

# =========================
# ⚽ OBTENER PARTIDOS
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
# 🎯 FILTRO SNIPER PRO
# =========================
def filtrar_partidos(partidos):
    filtrados = []

    for p in partidos:
        try:
            home = int(p.get("intHomeScore", 0))
            away = int(p.get("intAwayScore", 0))
            estado = p.get("strStatus", "")

            # ignorar terminados
            if "FT" in estado:
                continue

            # obtener minuto
            minuto = 0
            if "'" in estado:
                minuto = int(estado.replace("'", "").strip())

            total = home + away

            # 🔴 OVER SNIPER
            if 75 <= minuto <= 88 and home == away:
                p["tipo"] = "OVER SNIPER"
                filtrados.append(p)

            # 🟢 UNDER SNIPER
            elif minuto >= 70 and total <= 1:
                p["tipo"] = "UNDER SNIPER"
                filtrados.append(p)

        except:
            continue

    return filtrados[:2]  # máximo 2 picks

# =========================
# 🧠 ANALISIS IA
# =========================
def analizar_con_ia(partido):
    try:
        contexto = f"""
        Analiza este partido en vivo como experto en apuestas:

        Partido: {partido.get('strEvent')}
        Marcador: {partido.get('intHomeScore')} - {partido.get('intAwayScore')}
        Estado: {partido.get('strStatus')}
        Tipo: {partido.get('tipo')}

        Responde corto:
        - Confirmar si el pick tiene valor
        - Riesgo (bajo/medio/alto)
        """

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Eres un apostador profesional experto en apuestas en vivo."},
                {"role": "user", "content": contexto}
            ]
        }

        res = requests.post(url, headers=headers, json=data)

        if res.status_code != 200:
            return "⚠️ Error IA"

        json_res = res.json()
        return json_res["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error IA: {e}"

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
        enviar_telegram("⚠️ No hay partidos en vivo")
        return

    buenos = filtrar_partidos(partidos)

    if not buenos:
        return  # modo sniper: silencio si no hay edge

    for partido in buenos:
        analisis = analizar_con_ia(partido)

        mensaje = f"""
🎯 MODO SNIPER

{partido.get('strEvent')}
⏱️ {partido.get('strStatus')}
⚽ {partido.get('intHomeScore')} - {partido.get('intAwayScore')}

🔥 TIPO: {partido.get('tipo')}

{analisis}
"""
        enviar_telegram(mensaje)

# =========================
# ▶️ EJECUTAR
# =========================
if __name__ == "__main__":
    main()
