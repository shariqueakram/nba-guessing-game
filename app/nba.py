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

def build_filtered_player_list(min_minutes=4000):
    global filtered_players
    print("Building filtered player list...")

    all_players = players.get_active_players()
    good_players = []

    for p in all_players:
        player_id = p['id']
        name = p['full_name']

        try:
            stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=10)
            df = stats.get_data_frames()[0]
            career_row = df[df['SEASON_ID'] == 'Career']

            if career_row.empty:
                continue

            minutes = career_row['MIN'].fillna(0).values[0]
            if minutes > min_minutes:
                good_players.append({
                    'name': name,
                    'id': player_id,
                    'minutes': int(minutes)
                })

            time.sleep(2)  # slow down to avoid rate limits, i've increased it from .6 seconds

        except Exception as e:
            print(f"Skipping {name} due to error: {e}")
            time.sleep(2)

    filtered_players = good_players
    save_filtered_players(filtered_players)
    print(f"Filtered list built with {len(filtered_players)} players.")

def get_filtered_players():
    global filtered_players
    cached = load_filtered_players()
    if cached:
        print(f"Loaded {len(cached)} players from cache.")
        filtered_players = cached
    else:
        build_filtered_player_list()
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
