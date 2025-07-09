import os
import json
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Resolve absolute path for cache file (adjust if your script location differs)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # scripts/
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))  # one level up, 'app' folder expected here
CACHE_PATH = os.path.join(PROJECT_ROOT, "valid_players.json")

print(f"Caching to: {CACHE_PATH}")

# Load existing cache if exists
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        good_players = json.load(f)
    seen_ids = set(p['id'] for p in good_players)
    print(f"Loaded {len(good_players)} cached players.")
else:
    good_players = []
    seen_ids = set()
    print("Starting fresh cache.")

# Get all active players
all_players = players.get_active_players()
print(f"Total active players: {len(all_players)}")

for p in all_players:
    player_id = p['id']
    name = p['full_name']

    if player_id in seen_ids:
        # Already cached, skip
        continue

    try:
        print(f"Checking: {name} (ID: {player_id})")
        stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=10)
        df = stats.get_data_frames()[0]
        career_row = df[df['SEASON_ID'] == 'Career']

        if career_row.empty:
            print(f"No career data for {name}, skipping.")
            continue

        games_played = career_row['GP'].fillna(0).values[0]
        print(f"Games played for {name}: {games_played}")

        if games_played >= 82:
            player_data = {
                'name': name,
                'id': player_id,
                'games': int(games_played)
            }
            good_players.append(player_data)
            seen_ids.add(player_id)

            # Save cache after each new valid player
            print(f"Saving cache for {name}...")
            with open(CACHE_PATH, "w") as f:
                json.dump(good_players, f, indent=2)

            print(f"✅ Saved: {name} — {games_played} games")

        else:
            print(f"{name} has less than 82 games, skipping.")

        # Be kind to the API, sleep 2 seconds between calls
        time.sleep(2)

    except Exception as e:
        print(f"❌ Skipping {name} due to error: {e}")
        # Sleep longer on error to avoid flooding API
        time.sleep(5)

print(f"\n🎉 Done! Cached {len(good_players)} players.")
