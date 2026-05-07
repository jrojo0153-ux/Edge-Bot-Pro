# bot.py - Edge Bot Pro (Modo ESPN + Groq IA)
import os
import requests
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==========================================
# CONFIGURACIÓN DE VARIABLES DE ENTORNO
# ==========================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Validar variables críticas
if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
    logger.error("❌ TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID no configurados")
    raise EnvironmentError("Faltan credenciales de Telegram")

if not GROQ_API_KEY:
    logger.warning("⚠️ GROQ_API_KEY no configurada, el análisis con IA no funcionará")

# ==========================================
# FUNCIONES DE ARCHIVO
# ==========================================
def leer_aprendizaje():
    """Lee el archivo de aprendizaje histórico"""
    ruta = "data/aprendizaje.txt"
    try:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as file:
                contenido = file.read()
                logger.info(f"✅ Aprendizaje cargado: {len(contenido)} caracteres")
                return contenido
    except Exception as e:
        logger.error(f"❌ Error leyendo aprendizaje: {e}")
    return "No hay datos históricos previos."

def cargar_procesados():
    """Carga la lista de partidos ya procesados"""
    ruta = "data/procesados.txt"
    try:
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as file:
                procesados = file.read().splitlines()
                logger.info(f"✅ {len(procesados)} partidos en historial")
                return procesados
    except Exception as e:
        logger.error(f"❌ Error cargando procesados: {e}")
    return []

def guardar_procesado(partido_id):
    """Guarda un partido como procesado"""
    try:
        os.makedirs("data", exist_ok=True)
        with open("data/procesados.txt", "a", encoding="utf-8") as file:
            file.write(partido_id + "\n")
        logger.debug(f"✅ Partido guardado: {partido_id}")
    except Exception as e:
        logger.error(f"❌ Error guardando procesado: {e}")

# ==========================================
# FUNCIONES DE API
# ==========================================
def obtener_partidos_hoy():
    """Obtiene partidos de las 8 ligas top desde ESPN API"""
    logger.info("🔍 Buscando partidos en las 8 ligas top (ESPN API)...")
    partidos = []
    
    urls = [
        "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/mex.1/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/eng.1/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/esp.1/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/ita.1/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/ger.1/scoreboard",
        "https://site.api.espn.com/apis/site/v2/sports/soccer/fra.1/scoreboard"
    ]
    
    hoy = datetime.today().strftime('%Y-%m-%d')
    procesados = cargar_procesados()
    
    for url in urls:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "events" in data:
                for evento in data["events"]:
                    estado = evento.get("status", {}).get("type", {}).get("state", "")
                    
                    if estado == "pre":
                        try:
                            competitors = evento["competitions"][0]["competitors"]
                            home_team = next(c["team"]["name"] for c in competitors if c["homeAway"] == "home")
                            away_team = next(c["team"]["name"] for c in competitors if c["homeAway"] == "away")
                            liga = data.get("leagues", [{}])[0].get("name", "Liga desconocida")
                            
                            partido_str = f"LOCAL: {home_team} vs VISITANTE: {away_team} (Liga: {liga})"
                            partido_id = f"{hoy}_{home_team}_{away_team}".replace(" ", "_")
                            
                            if partido_id not in procesados:
                                partidos.append((partido_id, partido_str))
                                logger.debug(f"📅 Partido encontrado: {home_team} vs {away_team}")
                        except StopIteration:
                            logger.warning("⚠️ No se pudieron extraer equipos del evento")
                        except Exception as e:
                            logger.warning(f"⚠️ Error procesando evento: {e}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ Error al consultar ESPN ({url[:50]}...): {e}")
        except Exception as e:
            logger.error(f"❌ Error inesperado: {e}")
            
    logger.info(f"✅ {len(partidos)} partidos nuevos encontrados")
    return partidos[:5]  # Limitar a 5 para no saturar

def analizar_con_ia(historial, partido):
    """Analiza un partido usando Groq API"""
    if not GROQ_API_KEY:
        logger.warning("⚠️ Sin GROQ_API_KEY, usando análisis básico")
        return f"🏟️ Partido: {partido}\n⚖️ Veredicto: DESCARTADO (Sin API Key)"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    prompt = f"""[ROL Y OBJETIVO]
    Eres un Analista Cuantitativo (EDGE BOT PRO).
    Lee este historial de reglas:
    {historial}
    
    Analiza este partido: {partido}
    
    [REGLAS VITALES DE CÁLCULO Y ESTRATEGIA]
    1. Calcula la PROBABILIDAD REAL (X%).
    2. Calcula la CUOTA MÍNIMA RENTABLE dividiendo 100 entre tu Probabilidad.
    3. ESTRATEGIA AVANZADA: No te limites a decir quién gana. Debes proponer un Pick Principal (Ej: Gana Local, Empate No Acción) y OBLIGATORIAMENTE un Pick Secundario basado en Hándicaps Asiáticos (Ej: Visitante +1.5) o Totales de Goles/Puntos (Ej: Under 2.5, Over 210.5).
    4. Si no hay valor claro, tu Veredicto DEBE ser DESCARTADO.

    [FORMATO DE SALIDA ESTRICTO]
    PROHIBIDO escribir párrafos. Responde EXACTAMENTE con esta plantilla usando estos emojis:

    🏟️ Partido: [Nombre Local vs Nombre Visitante]
    🏆 Competición: [Nombre de la liga]
    🔍 Reglas Aplicadas: [Corchetes de las reglas usadas]
    🧠 Análisis Táctico: [1 sola oración técnica explicando el ritmo, bloque o ventaja]
    🎯 Pick Principal: [Mercado a apostar]
    ⚽ Pick Secundario: [Hándicap o Total de Goles/Puntos]
    📊 Probabilidad Real: [X%]
    💰 Cuota Mínima (+EV): [Calcula: 100 / X]
    ⚖️ Veredicto: [APROBADO o DESCARTADO]
    """
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "Eres un bot matemático. Eres directo, usas formato de lista y siempre buscas valor en mercados de goles y hándicaps."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        resultado = response.json()["choices"][0]["message"]["content"]
        logger.info("✅ Análisis IA completado")
        return resultado
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error de conexión con Groq: {e}")
        return f"🏟️ Partido: {partido}\n⚖️ Veredicto: DESCARTADO (Error API)"
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        return f"🏟️ Partido: {partido}\n⚖️ Veredicto: DESCARTADO (Error)"

def enviar_telegram(mensaje):
    """Envía mensaje a Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.error("❌ Credenciales de Telegram no configuradas")
        return False
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("✅ Mensaje enviado a Telegram")
            return True
        else:
            logger.error(f"❌ Error Telegram: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Excepción al enviar a Telegram: {e}")
        return False

# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================
def main():
    """Función principal del bot"""
    logger.info("🚀 Iniciando Edge Bot Pro (Predicciones)...")
    
    try:
        historial = leer_aprendizaje()
        partidos_nuevos = obtener_partidos_hoy()
        
        if not partidos_nuevos:
            logger.info("⏹️ No hay partidos nuevos sin procesar en esta hora.")
            return
            
        logger.info(f"📊 {len(partidos_nuevos)} partidos a analizar")
        
        for partido_id, partido_str in partidos_nuevos:
            logger.info(f"🔍 Analizando: {partido_str}")
            analisis = analizar_con_ia(historial, partido_str)
            
            guardar_procesado(partido_id)
            
            if "APROBADO" in analisis.upper():
                mensaje_final = f"""🤖 𝗘𝗗𝗚𝗘 𝗕𝗢𝗧 𝗣𝗥𝗢 (Alerta de Valor)
━━━━━━━━━━━━━━━━━━━━
{analisis}
━━━━━━━━━━━━━━━━━━━━"""
                enviar_telegram(mensaje_final)
                logger.info("✅ Pick APROBADO enviado a Telegram.")
            else:
                logger.info("❌ Pick DESCARTADO por la IA. No se envía a Telegram.")
            
            time.sleep(3)  # Rate limiting
            
        logger.info("🏁 Escaneo finalizado.")
        
    except KeyboardInterrupt:
        logger.info("⏹️ Bot detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error crítico en main: {e}")
        raise

if __name__ == "__main__":
    main()
