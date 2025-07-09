from fastapi import FastAPI
from app.nba import get_random_filtered_player_stats
from nba_api.stats.static import players

app = FastAPI()

@app.get("/player")
def get_player_stats():
    data = get_random_filtered_player_stats()
    if not data or 'error' in data:
        return data or {"error": "No stats available"}

    return {
        "id": data['id'],
        "stats": data['stats']
    }

@app.get("/reveal/{player_id}")
def reveal_player_name(player_id: int):
    player_list = players.get_active_players()
    for p in player_list:
        if p['id'] == player_id:
            return {"name": p['full_name']}
    return {"error": "Player not found"}
