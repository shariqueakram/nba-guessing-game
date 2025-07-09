# In your main.py or routes file
from fastapi import FastAPI
from app.nba import get_random_filtered_player_stats, get_player_by_name, search_players_by_name

app = FastAPI()

@app.get("/random-player")
async def get_random_player():
    player = get_random_filtered_player_stats(min_games=100, min_points=1000)
    if player:
        return player
    return {"error": "No suitable player found"}

@app.get("/player/{player_name}")
async def get_player(player_name: str):
    player = get_player_by_name(player_name)
    if player:
        return player
    return {"error": "Player not found"}

@app.get("/search/{search_term}")
async def search_players(search_term: str):
    return search_players_by_name(search_term)