import json
import os

FILE = "results.json"

def update_results():
    if not os.path.exists(FILE):
        return

    with open(FILE, "r") as f:
        data = json.load(f)

    # Aquí puedes luego conectar resultados reales
    for d in data:
        if "result" not in d:
            d["result"] = None

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
