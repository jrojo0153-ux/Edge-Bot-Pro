import json
import os

FILE = "results.json"

def save_results(data):
    if not os.path.exists(FILE):
        history = []
    else:
        with open(FILE, "r") as f:
            history = json.load(f)

    history.append(data)

    with open(FILE, "w") as f:
        json.dump(history, f, indent=2)
