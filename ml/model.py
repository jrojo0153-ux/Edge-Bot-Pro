# ml/model.py - Módulo de Modelos ML
import pandas as pd
import numpy as np
import joblib
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

from config import SPORTS

MODEL_DIR = "ml/models"
DATA_DIR = "data"
PENDING_FILE = "data/pendientes.csv"
HISTORICO_FILE = "data/Historico.csv"

# Crear carpetas si no existen
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# ==================== CLASE MODELO ====================
class SmartDummyModel:
    """Modelo simple que no depende de entrenamiento pesado"""
    
    def __init__(self, sport: str):
        self.sport = sport
        logger.debug(f"🔄 Modelo dummy inicializado para {sport}")
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        Genera probabilidades base según el deporte
        
        Returns:
            np.ndarray: Array de probabilidades [away, draw, home]
        """
        n = len(X)
        
        if SPORTS.get(self.sport, {}).get("has_draw", False):
            # Fútbol: away, draw, home
            return np.array([[0.38, 0.28, 0.34]] * n)
        else:
            # NBA / MLB: away, draw=0, home
            return np.array([[0.46, 0.00, 0.54]] * n)

# ==================== FUNCIONES DE MODELO ====================
def get_model_path(sport: str) -> str:
    """Obtiene la ruta del archivo del modelo"""
    return f"{MODEL_DIR}/model_{sport}.pkl"

def load_or_train_model(sport: str):
    """
    Carga el modelo existente o crea uno nuevo si falla
    
    Returns:
        tuple: (modelo, scaler) - scaler es None para modelo dummy
    """
    model_path = get_model_path(sport)
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            logger.info(f"✅ Modelo cargado para {sport}")
            return model, None
        except Exception as e:
            logger.warning(f"⚠️ Error cargando modelo: {e}. Creando nuevo...")
    
    logger.info(f"🔄 Creando modelo dummy para {sport}...")
    model = SmartDummyModel(sport)
    
    try:
        joblib.dump(model, model_path)
        logger.info(f"✅ Modelo guardado en {model_path}")
    except Exception as e:
        logger.error(f"❌ Error guardando modelo: {e}")
    
    return model, None

def predict_proba(match: dict, model, scaler, sport: str) -> dict:
    """
    Predicción usando el modelo con validación de datos
    
    Args:
        match: Diccionario con datos del partido
        model: Modelo cargado
        scaler: Scaler (None para dummy)
        sport: Código del deporte
    
    Returns:
        dict: Probabilidades por outcome
    """
    try:
        # Validar que el match tenga odds válidas
        if not match.get("odds"):
            logger.warning(f"⚠️ Match sin odds: {match.get('home')} vs {match.get('away')}")
            return {"home": 0.5, "away": 0.5, "draw": 0.0}
        
        probs = model.predict_proba([[0]])[0]
        
        has_draw = SPORTS[sport]["has_draw"]
        
        if has_draw:
            return {
                "home": round(probs[2], 3), 
                "draw": round(probs[1], 3), 
                "away": round(probs[0], 3)
            }
        else:
            p_home, p_away = probs[2], probs[0]
            total = p_home + p_away + 1e-8
            return {
                "home": round(p_home / total, 3), 
                "away": round(p_away / total, 3), 
                "draw": 0.0
            }
            
    except Exception as e:
        logger.error(f"❌ Error en predict_proba: {e}")
        return {"home": 0.5, "away": 0.5, "draw": 0.0}

# ==================== FUNCIONES DE AUDITORÍA ====================
def guardar_picks_enviados(parlays: list) -> None:
    """Guarda los picks enviados en pendientes.csv para auditoría"""
    nuevos_pendientes = []
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for parlay in parlays:
        for leg in parlay["legs"]:
            nuevos_pendientes.append({
                "fecha": fecha_hoy,
                "id_partido": leg.get("id", "N/A"),
                "deporte": leg["sport"],
                "encuentro": leg["match"],
                "prediccion": leg["pick"],
                "cuota": leg["odds"],
                "resultado_real": "PENDIENTE"
            })
    
    if nuevos_pendientes:
        try:
            df = pd.DataFrame(nuevos_pendientes)
            header = not os.path.exists(PENDING_FILE)
            df.to_csv(PENDING_FILE, mode='a', index=False, header=header)
            logger.info(f"💾 {len(nuevos_pendientes)} picks guardados para auditoría.")
        except Exception as e:
            logger.error(f"❌ Error guardando picks: {e}")

def audit_and_learn(api_key: str = None) -> None:
    """Mueve los pendientes al histórico (Simulación de aprendizaje)"""
    if not os.path.exists(PENDING_FILE):
        logger.info("ℹ️ No hay picks pendientes.")
        return

    try:
        df_pendientes = pd.read_csv(PENDING_FILE)
        
        # Aquí irá la lógica de consulta a /scores en el futuro
        header = not os.path.exists(HISTORICO_FILE)
        df_pendientes.to_csv(HISTORICO_FILE, mode='a', index=False, header=header)
        
        os.remove(PENDING_FILE)
        logger.info("✅ Auditoría completada: Picks movidos al histórico.")
        
    except Exception as e:
        logger.error(f"❌ Error en auditoría: {e}")
