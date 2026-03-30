import requests

# 🔐 CONFIG (PON TUS DATOS)
TELEGRAM_TOKEN = "8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE"
CHAT_ID = "8536626773"
OPENAI_API_KEY = "sk-proj-tHBA53SOzLN28IoPrAUFXJd9dixuhA8KfsWdkD6qRxNEDmjJllK1PRPVpbmw898FwK0Nc-nJAUT3BlbkFJT0IS7EihY3qYdpe6fDZULeLsHrowAKc_ecqF3"

# ⚽ Obtener partidos en vivo (VERSIÓN ESTABLE)
def obtener_partidos():
    url = "https://www.thesportsdb.com/api/v1/json/3/livescore.php?s=Soccer"

    try:
        res = requests.get(url)

        if res.status_code != 200:
            return []

        data = res.json()

        return data.get("events", []) if data else []

    except Exception as e:
        return []

# 🧠 FILTROS PRO
def filtrar_partidos(partidos):
    filtrados = []

    for p in partidos:
        try:
            home = int(p.get("intHomeScore", 0))
            away = int(p.get("intAwayScore", 0))
            estado = p.get("strStatus", "")

            # ❌ ignorar partidos terminados
            if "FT" in estado:
                continue

            total_goles = home + away

            # 🎯 FILTRO (pocos goles = posible UNDER)
            if total_goles <= 2:
                filtrados.append(p)

        except:
            continue

    return filtrados[:3]  # máximo 3 partidos

# 🧠 ANALISIS IA (PROTEGIDO)
def analizar_con_ia(partido):
    try:
        contexto = f"""
        Analiza este partido en vivo como experto en apuestas:

        Partido: {partido.get('strEvent')}
        Marcador: {partido.get('intHomeScore')} - {partido.get('intAwayScore')}
        Estado: {partido.get('strStatus')}

        Responde:
        - Ritmo (lento o alto)
        - Mejor apuesta (UNDER / OVER / NO APOSTAR)
        - Explicación corta
        """

        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "Eres un analista experto en apuestas deportivas en vivo."},
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

# 📲 ENVIAR A TELEGRAM
def enviar_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

def main():
    partidos = obtener_partidos()

    if not partidos:
        enviar_telegram("⚠️ No hay partidos en vivo")
        return

    buenos = filtrar_partidos(partidos)

    if not buenos:
        enviar_telegram("⚠️ No hay partidos con edge ahora")
        return

    for partido in buenos:
        analisis = analizar_con_ia(partido)

        mensaje = f"""
🔥 ALERTA EDGE

{partido.get('strEvent')}
{partido.get('intHomeScore')} - {partido.get('intAwayScore')}

{analisis}
"""
        enviar_telegram(mensaje)

# ▶️ EJECUTAR
if __name__ == "__main__":
    main()
