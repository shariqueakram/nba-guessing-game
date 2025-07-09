# scripts/build_player_cache.py
import json
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

CACHE_FILE = "app/valid_players.json"

def build_filtered_player_list(min_minutes=4000):
    all_players = players.get_active_players()
    good_players = []

    for p in all_players:
        player_id = p['id']
        name = p['full_name']

        try:
            print(f"Checking: {name}")
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

            time.sleep(2)  # More conservative delay

        except Exception as e:
            print(f"Skipping {name} due to error: {e}")
            time.sleep(3)

    with open(CACHE_FILE, "w") as f:
        json.dump(good_players, f)
    print(f"Saved {len(good_players)} players to cache.")

if __name__ == "__main__":
    build_filtered_player_list()
