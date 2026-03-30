import os
import requests

def send_telegram_message(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("❌ Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        requests.post(url, json={
            "chat_id": chat_id,
            "text": message
        })
        print("📲 Enviado a Telegram")
    except Exception as e:
        print("❌ Error Telegram:", e)
