import json
import os
from datetime import datetime

FILE = "ml/picks.json"

def save_picks(picks):
    data = []

    if os.path.exists(FILE):
        with open(FILE) as f:
            data = json.load(f)

    for p in picks:
        data.append({
            **p,
            "date": str(datetime.now()),
            "result": None
        })

    with open(FILE, "w") as f:
        json.dump(data, f, indent=2)
