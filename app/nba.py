import json
import os
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

CACHE_FILE = "app/valid_players.json"  # relative to your project root

filtered_players = []

def save_filtered_players(players_list):
    with open(CACHE_FILE, "w") as f:
        json.dump(players_list, f)

def load_filtered_players():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return None

def get_filtered_players():
    global filtered_players
    if not filtered_players:
        filtered_players = load_filtered_players()
    return filtered_players


def get_random_filtered_player_stats():
    import random

    players_list = get_filtered_players()
    if not players_list:
        return {"error": "No players available"}

    player = random.choice(players_list)
    player_id = player['id']
    name = player['name']

    try:
        stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=10)
        df = stats.get_data_frames()[0]
        career_row = df[df['SEASON_ID'] == 'Career']

        return {
            'name': name,
            'id': player_id,
            'stats': {
                'points': int(career_row['PTS'].fillna(0).values[0]),
                'rebounds': int(career_row['REB'].fillna(0).values[0]),
                'assists': int(career_row['AST'].fillna(0).values[0]),
                'games': int(career_row['GP'].fillna(0).values[0]),
                'minutes': int(career_row['MIN'].fillna(0).values[0]),
            }
        }

    except Exception as e:
        print(f"Error retrieving stats for {name}: {e}")
        return {"error": "Failed to fetch player stats"}
