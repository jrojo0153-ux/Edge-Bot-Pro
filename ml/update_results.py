import json
import os
from ml.model import save_result

FILE = "ml/picks.json"

def update_results():
    if not os.path.exists(FILE):
        return

    with open(FILE) as f:
        data = json.load(f)

    for p in data:
        if p["result"] is None:
            # 🔥 simulación (puedes conectar API real luego)
            result = 1 if p["odds"] < 2 else 0
            p["result"] = result
            save_result(p, result)

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
