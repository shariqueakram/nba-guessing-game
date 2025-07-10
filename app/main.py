# ... (previous imports remain the same)

# Load valid players with enhanced data
try:
    with open("valid_players.json", "r") as f:
        VALID_PLAYERS = json.load(f)
except FileNotFoundError:
    VALID_PLAYERS = []

# ... (previous middleware and models remain the same)

@app.get("/game/new")
async def new_game():
    """Start a new game with enhanced player data"""
    try:
        if not VALID_PLAYERS:
            raise HTTPException(status_code=500, detail="No valid players found")
        
        random_player = random.choice(VALID_PLAYERS)
        
        # Return stats without the name for guessing
        return {
            "player_id": random_player["id"],
            "stats": random_player["stats"],
            "teams": random_player.get("teams", []),
            "hint": f"This player has played {random_player['stats']['games']} games for {len(random_player.get('teams', []))} teams"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting new game: {str(e)}")

# ... (other endpoints remain similar but will use the enhanced data)