import os
import requests

TOKEN = os.getenv("8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE")
CHAT_ID = os.getenv("8536626773")

def send_telegram_message(msg):
    if not TOKEN or not CHAT_ID:
        print("❌ Telegram no configurado")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, json={
        "chat_id": CHAT_ID,
        "text": msg
    })
