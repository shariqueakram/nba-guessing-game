import os
import json
import time
from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats

# Absolute path to valid_players.json
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_PATH = os.path.join(PROJECT_ROOT, "app", "valid_players.json")

# Ensure 'app' folder exists
os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)

# Load cache if it exists
if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH, "r") as f:
        good_players = json.load(f)
    seen_ids = set(p['id'] for p in good_players)
    print(f"Loaded {len(good_players)} cached players.")
else:
    good_players = []
    seen_ids = set()

# Get all active NBA players
all_players = players.get_active_players()

for p in all_players:
    player_id = p['id']
    name = p['full_name']

    if player_id in seen_ids:
        continue  # already saved

    try:
        print(f"Checking: {name}")
        stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=10)
        df = stats.get_data_frames()[0]
        career_row = df[df['SEASON_ID'] == 'Career']

        if career_row.empty:
            continue

        games_played = career_row['GP'].fillna(0).values[0]
        if games_played >= 82:
            player_data = {
                'name': name,
                'id': player_id,
                'games': int(games_played)
            }
            good_players.append(player_data)
            seen_ids.add(player_id)

            # Save after each success
            with open(CACHE_PATH, "w") as f:
                json.dump(good_players, f, indent=2)

            print(f"✅ Saved: {name} — {games_played} games")

        time.sleep(2)  # be respectful to NBA servers

    except Exception as e:
        print(f"❌ Skipping {name} due to error: {e}")
        time.sleep(3)

print(f"\n🎉 Done! Saved {len(good_players)} players to {CACHE_PATH}")