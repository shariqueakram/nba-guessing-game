from fastapi import FastAPI
from app.nba import get_random_player_and_stats

app = FastAPI()

@app.get("/player") # Adding decorator for the endpoints of FastAPI
def get_player_stats():
    data = get_random_player_and_stats()
    if not data:
        return {"error": "No stats available, try again"}
    
    return {
        "id": data['id'],
        "stats": data['stats']
    }

@app.get("/reveal/{player_id}")
def reveal_player_name(player_id: int):
    from nba_api.stats.static import players
    player_list = players.get_active_players()
    for p in player_list:
        if p['id'] == player_id:
            return {"name": p['full_name']}
    return {"error": "Player not found"}
