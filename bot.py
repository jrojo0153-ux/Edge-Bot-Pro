import requests

TOKEN = "8725696882:AAEaz3TJ0KM2VC5q_gXWgqcNb694FN6XWaE"
CHAT_ID = "8536626773"

def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    requests.post(url, data=data)

def detectar_edge():
    # Simulación (luego lo mejoramos)
    mensaje = """🔥 ALERTA EDGE

🏀 Celtics vs Hornets
Min 52 | 98-85

👉 Ritmo alto
👉 Defensa débil

💰 Pick:
Over 210.5
Confianza: Alta
"""
    enviar_mensaje(mensaje)

if __name__ == "__main__":
    detectar_edge()
