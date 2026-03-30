import requests

def get_matches():
    url = "https://api.sofascore.com/api/v1/sport/football/events/live"

    try:
        res = requests.get(url)
        data = res.json()

        matches = []

        for event in data.get("events", []):
            home = event["homeTeam"]["name"]
            away = event["awayTeam"]["name"]
            event_id = event["id"]

            matches.append({
                "id": event_id,
                "home": home,
                "away": away
            })

        return matches

    except:
        return []
