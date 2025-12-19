# download_moneypuck_data.py - Automatically download all player data
import requests
import pandas as pd
import time
from pathlib import Path

# Create data folder if it doesn't exist
DATA_FOLDER = Path("data_gbg")
DATA_FOLDER.mkdir(exist_ok=True)

# MoneyPuck URL pattern (adjust if needed)
# Format: https://moneypuck.com/moneypuck/playerData/careers/gameByGame/8471214.csv
BASE_URL = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/{player_id}.csv"

def download_player_data(player_id, player_name=None):
    """Download game-by-game data for a single player"""
    url = BASE_URL.format(player_id=player_id)
    filename = DATA_FOLDER / f"{player_id}.csv"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save the CSV
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        name = player_name if player_name else player_id
        print(f"✅ Downloaded: {name} ({player_id})")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed: {player_id} - {e}")
        return False

def get_all_player_ids():
    """
    Get list of all active NHL players
    You have several options here:
    """
    
    # OPTION 1: Manual list of player IDs you care about
    # Get these from MoneyPuck or NHL API
    player_ids = [
        8478402,  # Connor McDavid
        8479318,  # Auston Matthews
        8476883,  # Nathan MacKinnon
        8477492,  # Leon Draisaitl
        8478483,  # Nikita Kucherov
        # ... add more
    ]
    
    # OPTION 2: Load from a CSV file
    # Uncomment this if you have a player_ids.csv file
    # df = pd.read_csv("player_ids.csv")
    # player_ids = df['playerId'].tolist()
    
    # OPTION 3: Scrape from MoneyPuck's player list page
    # (Would need BeautifulSoup - see below)
    
    return player_ids

def download_all_players():
    """Download data for all players"""
    player_ids = get_all_player_ids()
    
    print(f"📥 Starting download for {len(player_ids)} players...")
    print(f"📂 Saving to: {DATA_FOLDER.absolute()}\n")
    
    success_count = 0
    fail_count = 0
    
    for i, player_id in enumerate(player_ids, 1):
        print(f"[{i}/{len(player_ids)}] ", end="")
        
        if download_player_data(player_id):
            success_count += 1
        else:
            fail_count += 1
        
        # Be nice to the server - wait between requests
        time.sleep(0.5)
    
    print(f"\n{'='*50}")
    print(f"✅ Successfully downloaded: {success_count}")
    print(f"❌ Failed: {fail_count}")
    print(f"📂 Files saved to: {DATA_FOLDER.absolute()}")

if __name__ == "__main__":
    download_all_players()