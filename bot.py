import requests

OPENAI_API_KEY = "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"
TOKEN = "8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE"
CHAT_ID = "8536626773"

def preguntar_ia(contexto):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Eres un analista de apuestas deportivas experto en detectar edge en vivo."},
            {"role": "user", "content": contexto}
        ]
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()["choices"][0]["message"]["content"]

def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def main():
    # EJEMPLO (luego conectamos datos reales)
    contexto = """
    Partido: Celtics vs Hornets
    Minuto: 52
    Marcador: 98-85
    Ritmo: alto
    """

    respuesta = preguntar_ia(contexto)
    enviar_telegram(respuesta)

if __name__ == "__main__":
    main()
