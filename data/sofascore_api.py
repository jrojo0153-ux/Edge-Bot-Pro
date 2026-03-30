import requests

def get_team_rating(team):
    try:
        url = "https://api.sofascore.com/api/v1/search/all"
        res = requests.get(url, params={"q": team})
        
        if res.status_code != 200:
            return 0.5

        # 🔥 fallback simple (puedes mejorar luego)
        return 0.5

    except:
        return 0.5
