import json
import os

FILE = "ml/data.json"

def load():
    if not os.path.exists(FILE):
        return []
    with open(FILE) as f:
        return json.load(f)

def save_result(pick, result):
    data = load()

    data.append({
        "match": pick["match"],
        "pick": pick["pick"],
        "odds": pick["odds"],
        "result": result
    })

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_winrate():
    data = load()
    if not data:
        return 0.5

    wins = sum(1 for d in data if d["result"] == 1)
    return wins / len(data)
