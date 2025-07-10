from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
import time
import random
from typing import Dict, List, Optional

# Configuration
REQUEST_DELAY = 1.5  # Seconds between API calls
MAX_RETRIES = 3

def get_player_with_retry(player_id: int):
    """Handles rate limits and retries"""
    for attempt in range(MAX_RETRIES):
        try:
            # Randomize delay to avoid patterns
            time.sleep(REQUEST_DELAY + random.uniform(0, 1))
            
            # Fetch data
            career = playercareerstats.PlayerCareerStats(
                player_id=player_id,
                timeout=30,
                proxy='https://proxy.example.com'  # Optional proxy
            )
            return career.get_data_frames()[0]  # Regular season stats
            
        except Exception as e:
            if attempt == MAX_RETRIES - 1:
                print(f"Failed after {MAX_RETRIES} attempts for player {player_id}: {e}")
                return None
            time.sleep(5 * (attempt + 1))  # Exponential backoff

def get_player_stats(player_id: int, player_name: str) -> Optional[Dict]:
    """Gets stats with proper error handling"""
    try:
        df = get_player_with_retry(player_id)
        if df is None:
            return None
            
        career_row = df[df['SEASON_ID'] == 'Career']
        
        if not career_row.empty:
            return {
                'name': player_name,
                'id': player_id,
                'teams': list(set(df[df['TEAM_ABBREVIATION'].notna()]['TEAM_ABBREVIATION'])),
                'stats': {
                    'games': int(career_row['GP'].iloc[0]),
                    'points': int(career_row['PTS'].iloc[0]),
                    'rebounds': int(career_row['REB'].iloc[0]),
                    'assists': int(career_row['AST'].iloc[0]),
                    'fg_pct': float(career_row['FG_PCT'].iloc[0]),
                    'three_pct': float(career_row['FG3_PCT'].iloc[0]),
                    'ft_pct': float(career_row['FT_PCT'].iloc[0])
                }
            }
    except Exception as e:
        print(f"Error processing {player_name}: {e}")
    return None

def get_random_player(min_games=100, min_points=1000):
    """Gets a random eligible player"""
    all_players = players.get_players()
    random.shuffle(all_players)  # Avoid hitting same players first
    
    for player in all_players:
        stats = get_player_stats(player['id'], player['full_name'])
        if stats and stats['stats']['games'] >= min_games and stats['stats']['points'] >= min_points:
            return stats
        time.sleep(REQUEST_DELAY)
    
    return None