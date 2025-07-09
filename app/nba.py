from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
import pandas as pd
import random
from typing import Dict, Any, Optional


def get_all_players():
    """Get all NBA players from the static data"""
    return players.get_players()


def get_player_career_stats(player_id: str, name: str) -> Dict[str, Any]:
    """
    Get career stats for a specific NBA player
    
    Args:
        player_id (str): NBA player ID
        name (str): Player name
    
    Returns:
        dict: Player stats dictionary with name, id, and career stats
    """
    try:
        stats = playercareerstats.PlayerCareerStats(player_id=player_id, timeout=10)
        data_frames = stats.get_data_frames()
        
        if not data_frames:
            raise ValueError("No data frames returned")
        
        df = data_frames[0]
        
        if df.empty:
            raise ValueError("DataFrame is empty")

        # Try to find 'Career' row
        career_row = df[df['SEASON_ID'] == 'Career']

        if not career_row.empty:
            # 'Career' row exists — use it directly
            return {
                'name': name,
                'id': player_id,
                'stats': {
                    'points': int(career_row['PTS'].fillna(0).values[0]),
                    'rebounds': int(career_row['REB'].fillna(0).values[0]),
                    'assists': int(career_row['AST'].fillna(0).values[0]),
                    'games': int(career_row['GP'].fillna(0).values[0]),
                    'minutes': int(career_row['MIN'].fillna(0).values[0])
                }
            }

        # 🚨 Fallback: Manually sum all seasons
        totals = df.select_dtypes(include='number').sum(numeric_only=True)

        return {
            'name': name,
            'id': player_id,
            'stats': {
                'points': int(totals.get('PTS', 0)),
                'rebounds': int(totals.get('REB', 0)),
                'assists': int(totals.get('AST', 0)),
                'games': int(totals.get('GP', 0)),
                'minutes': int(totals.get('MIN', 0))
            }
        }
    
    except Exception as e:
        print(f"Error fetching stats for player {player_id}: {e}")
        return {
            'name': name,
            'id': player_id,
            'stats': {
                'points': 0,
                'rebounds': 0,
                'assists': 0,
                'games': 0,
                'minutes': 0
            }
        }


def filter_players_by_criteria(players_list: list, min_games: int = 100, min_points: int = 1000) -> list:
    """
    Filter players based on minimum games played and career points
    
    Args:
        players_list (list): List of all players
        min_games (int): Minimum games played
        min_points (int): Minimum career points
    
    Returns:
        list: Filtered list of players who meet the criteria
    """
    filtered_players = []
    
    for player in players_list:
        try:
            player_stats = get_player_career_stats(str(player['id']), player['full_name'])
            
            if (player_stats['stats']['games'] >= min_games and 
                player_stats['stats']['points'] >= min_points):
                filtered_players.append(player_stats)
                
        except Exception as e:
            print(f"Error processing player {player['full_name']}: {e}")
            continue
    
    return filtered_players


def get_random_filtered_player_stats(min_games: int = 100, min_points: int = 1000) -> Optional[Dict[str, Any]]:
    """
    Get a random NBA player that meets the filtering criteria
    
    Args:
        min_games (int): Minimum games played
        min_points (int): Minimum career points
    
    Returns:
        dict: Random player's stats or None if no players found
    """
    try:
        all_players = get_all_players()
        
        if not all_players:
            return None
        
        # For performance, we'll randomly sample players instead of filtering all
        # This is more efficient for a guessing game
        max_attempts = 50  # Prevent infinite loop
        attempts = 0
        
        while attempts < max_attempts:
            random_player = random.choice(all_players)
            
            try:
                player_stats = get_player_career_stats(str(random_player['id']), random_player['full_name'])
                
                if (player_stats['stats']['games'] >= min_games and 
                    player_stats['stats']['points'] >= min_points):
                    return player_stats
                    
            except Exception as e:
                print(f"Error processing random player {random_player['full_name']}: {e}")
            
            attempts += 1
        
        print(f"Could not find a suitable player after {max_attempts} attempts")
        return None
        
    except Exception as e:
        print(f"Error in get_random_filtered_player_stats: {e}")
        return None


def get_player_by_name(player_name: str) -> Optional[Dict[str, Any]]:
    """
    Get player stats by name
    
    Args:
        player_name (str): Player's full name
    
    Returns:
        dict: Player stats or None if not found
    """
    try:
        all_players = get_all_players()
        
        # Find player by name (case insensitive)
        for player in all_players:
            if player['full_name'].lower() == player_name.lower():
                return get_player_career_stats(str(player['id']), player['full_name'])
        
        return None
        
    except Exception as e:
        print(f"Error finding player {player_name}: {e}")
        return None


def search_players_by_name(search_term: str, limit: int = 10) -> list:
    """
    Search for players by name (partial match)
    
    Args:
        search_term (str): Search term
        limit (int): Maximum number of results
    
    Returns:
        list: List of matching players
    """
    try:
        all_players = get_all_players()
        matching_players = []
        
        search_term_lower = search_term.lower()
        
        for player in all_players:
            if search_term_lower in player['full_name'].lower():
                matching_players.append({
                    'id': player['id'],
                    'name': player['full_name'],
                    'years_active': f"{player.get('from_year', 'N/A')}-{player.get('to_year', 'N/A')}"
                })
                
                if len(matching_players) >= limit:
                    break
        
        return matching_players
        
    except Exception as e:
        print(f"Error searching players: {e}")
        return []