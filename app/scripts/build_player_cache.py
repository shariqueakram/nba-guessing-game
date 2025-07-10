from app.nba import get_player_stats
import json
import time

def build_cache(output_file="app/valid_players.json", min_games=82):
    active_players = [
        p for p in players.get_active_players() 
        if not p['full_name'].endswith('(TW)')  # Filter two-way players
    ]
    
    valid_players = []
    
    for player in active_players[:50]:  # Test with 50 players first
        print(f"Processing {player['full_name']}...")
        stats = get_player_stats(player['id'], player['full_name'])
        
        if stats and stats['stats']['games'] >= min_games:
            valid_players.append(stats)
            # Save incremental progress
            with open(output_file, 'w') as f:
                json.dump(valid_players, f, indent=2)
        
        time.sleep(1.5)  # Critical for rate limiting

if __name__ == "__main__":
    build_cache()