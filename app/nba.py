from nba_api.stats.static import players
from nba_api.stats.endpoints import playercareerstats
import random

def get_random_player_and_stats():
    all_players = players.get_active_players()
    player = random.choice(all_players)
    player_id = player['id']
    name = player['full_name']

    stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_data = stats.get_data_frames()[0]
    
    total_stats = career_data[career_data['SEASON_ID'] == 'Career']

    if total_stats.empty:
        return None  # Retry logic later

    return {
        'name': name,
        'id': player_id,
        'stats': {
            'points': int(total_stats['PTS'].values[0]),
            'rebounds': int(total_stats['REB'].values[0]),
            'assists': int(total_stats['AST'].values[0]),
            'games': int(total_stats['GP'].values[0]),
        }
    }
