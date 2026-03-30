import json
import os

FILE_PATH = "results.json"


def save_results(data):
    """
    Guarda resultados históricos del bot
    """

    try:
        # Si el archivo no existe → crear lista
        if not os.path.exists(FILE_PATH):
            history = []
        else:
            with open(FILE_PATH, "r") as f:
                history = json.load(f)

        history.append(data)

        with open(FILE_PATH, "w") as f:
            json.dump(history, f, indent=2)

        print("💾 Resultados guardados")

    except Exception as e:
        print("❌ Error guardando resultados:", e)
