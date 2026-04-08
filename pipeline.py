from data.odds_api import get_odds
# Cambiamos la importación para usar el nuevo sistema de IA
from ml.model import cargar_modelo, entrenar_modelo, predecir
# Mantener tus otros módulos
from ml.storage import save_results
from ml.update_results import update_results
from utils.telegram import send_telegram_message
from datetime import datetime
import os

def run_pipeline():
    print("🚀 INICIANDO EDGE BOT PRO (MODO IA)")

    # 1. Actualizar resultados previos
    try:
        update_results()
    except:
        print("⚠️ No se pudo actualizar resultados previos, continuando...")

    # 2. Cargar el modelo entrenado con tu Historico.csv
    # Si no existe, lo entrena en el momento
    modelo = cargar_modelo() or entrenar_modelo()

    # 3. Obtener partidos de la API
    matches = get_odds()
    if not matches:
        print("❌ No se obtuvieron partidos de la API")
        return

    picks = []

    for match in matches:
        # Usamos la nueva función 'predecir' que creamos en ml/model.py
        probs = predecir(modelo, {
            "home_odds": match["odds"].get("home", 1.0),
            "away_odds": match["odds"].get("away", 1.0)
        })

        if not probs:
            continue

        for outcome in ["home", "draw", "away"]:
            odd = match["odds"].get(outcome)
            
            # FILTRO DE SEGURIDAD: Si la cuota es > 10.0 (como en tu reporte), la ignoramos
            if not odd or odd > 10.0:
                continue

            prob = probs[outcome]
            implied = 1 / odd
            edge = prob - implied

            # FILTRO DE VALOR: Solo picks con Edge positivo real
            if edge > 0.05: # Umbral mínimo de 5% para entrar a la lista
                picks.append({
                    "match_id": match["id"],
                    "match": f"{match['home']} vs {match['away']}",
                    "pick": outcome,
                    "odds": odd,
                    "edge": edge
                })

    # Ordenar por edge (Mejores oportunidades primero)
    picks = sorted(picks, key=lambda x: x["edge"], reverse=True)

    # Filtrar 1 pick por partido para no duplicar riesgo
    unique = []
    used = set()
    for p in picks:
        if p["match_id"] not in used:
            unique.append(p)
            used.add(p["match_id"])
    picks = unique[:10]

    if len(picks) < 2:
        print("❌ No hay suficientes picks con valor (Edge) suficiente.")
        return

    # --- GENERACIÓN DE PARLAYS ---
    conservador = picks[:2]
    balanceado = picks[:4]
    agresivo = picks[:6]

    def calc(parlay):
        total = 1
        for p in parlay:
            total *= p["odds"]
        return round(total, 2)

    def format_parlay(name, parlay):
        if not parlay: return ""
        text = f"\n{name}:\n"
        for p in parlay:
            text += f"• {p['match']} → {p['pick']} (C: {p['odds']} | E: {round(p['edge'],3)})\n"
        text += f"💰 Cuota Total: {calc(parlay)}\n"
        return text

    msg = "🔥 *EDGE BOT PRO - IA REPORT*\n"
    msg += format_parlay("🛡️ CONSERVADOR", conservador)
    msg += format_parlay("⚖️ BALANCEADO", balanceado)
    msg += format_parlay("💣 AGRESIVO", agresivo)

    print(msg)

    # Enviar a Telegram
    try:
        send_telegram_message(msg)
    except Exception as e:
        print(f"❌ Error enviando mensaje: {e}")

    # Guardar bitácora
    save_results({
        "date": str(datetime.now()),
        "picks": picks
    })

if __name__ == "__main__":
    run_pipeline()
