# download_all_moneypuck_players.py - Get ALL players automatically
import requests
import pandas as pd
import time
from pathlib import Path

DATA_FOLDER = Path("data_gbg")
DATA_FOLDER.mkdir(exist_ok=True)

BASE_URL = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/{player_id}.csv"

def get_all_player_ids_from_moneypuck():
    """
    Fetch player list from MoneyPuck's skater stats
    This gets ALL players who have played in recent seasons
    """
    print("📋 Fetching player list from MoneyPuck...\n")
    
    # MoneyPuck's all-situations skater stats (has player IDs)
    # Adjust seasons as needed (2023 = 2023-24 season)
    stats_url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2023/regular/skaters.csv"
    
    try:
        # Download season summary to get player IDs
        df = pd.read_csv(stats_url)
        
        player_ids = df['playerId'].unique().tolist()
        player_names = dict(zip(df['playerId'], df['name']))
        
        print(f"✅ Found {len(player_ids)} players from 2023-24 season\n")
        return player_ids, player_names
        
    except Exception as e:
        print(f"❌ Error fetching player list: {e}")
        return [], {}

def get_multi_season_players():
    """Get players from multiple seasons (more comprehensive)"""
    print("📋 Fetching players from multiple seasons...\n")
    
    all_players = {}
    seasons = [2023, 2022, 2021, 2020, 2019]  # Last 5 seasons
    
    for season in seasons:
        url = f"https://moneypuck.com/moneypuck/playerData/seasonSummary/{season}/regular/skaters.csv"
        try:
            df = pd.read_csv(url)
            for _, row in df.iterrows():
                all_players[row['playerId']] = row['name']
            print(f"  ✅ {season}-{season+1}: {len(df)} players")
            time.sleep(1)  # Be nice to the server
        except Exception as e:
            print(f"  ❌ {season}-{season+1}: Failed - {e}")
    
    print(f"\n✅ Total unique players: {len(all_players)}\n")
    return list(all_players.keys()), all_players

def download_player_data(player_id, player_name=None):
    """Download game-by-game data for a single player"""
    url = BASE_URL.format(player_id=player_id)
    filename = DATA_FOLDER / f"{player_id}.csv"
    
    # Skip if already downloaded
    if filename.exists():
        print(f"⏭️  Skipped (exists): {player_name or player_id}")
        return True
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Check if file has content
        if len(response.content) < 100:  # Too small = no data
            print(f"⚠️  No data: {player_name or player_id}")
            return False
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Downloaded: {player_name or player_id}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {player_name or player_id} - {str(e)[:50]}")
        return False

def download_all():
    """Main function to download all player data"""
    
    # Choose your method:
    # Option A: Just current season
    # player_ids, player_names = get_all_player_ids_from_moneypuck()
    
    # Option B: Last 5 seasons (recommended - gets more players)
    player_ids, player_names = get_multi_season_players()
    
    if not player_ids:
        print("❌ No players found!")
        return
    
    print(f"📥 Starting download for {len(player_ids)} players...")
    print(f"📂 Saving to: {DATA_FOLDER.absolute()}\n")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    for i, player_id in enumerate(player_ids, 1):
        player_name = player_names.get(player_id, str(player_id))
        print(f"[{i}/{len(player_ids)}] ", end="")
        
        result = download_player_data(player_id, player_name)
        
        if result:
            success_count += 1
        else:
            fail_count += 1
        
        # Rate limiting - be nice to MoneyPuck's servers
        time.sleep(0.3)
    
    print(f"\n{'='*60}")
    print(f"✅ Successfully downloaded: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📂 Files saved to: {DATA_FOLDER.absolute()}")
    print(f"\n💡 Next step: Run 'python build_players_game_by_game.py'")

if __name__ == "__main__":
    download_all()
