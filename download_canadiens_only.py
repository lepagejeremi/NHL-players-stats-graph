# download_canadiens_only.py - Télécharger seulement les joueurs des Canadiens
import requests
import pandas as pd
import time
from pathlib import Path

DATA_FOLDER = Path("data_gbg")
DATA_FOLDER.mkdir(exist_ok=True)

BASE_URL = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/regular/skaters/{player_id}.csv"

def get_canadiens_players():
    """Get current Montreal Canadiens roster"""
    print("🔴⚪🔵 Fetching Montreal Canadiens players...\n")
    
    # Get 2024-25 season data
    url = "https://moneypuck.com/moneypuck/playerData/seasonSummary/2024/regular/skaters.csv"
    
    try:
        df = pd.read_csv(url)
        
        # Filter for Montreal (team abbreviation is "MTL" or "MON")
        canadiens = df[df['team'].isin(['MTL', 'MON'])].copy()
        
        if len(canadiens) == 0:
            print("⚠️  Trying alternative team codes...")
            # Sometimes it's stored differently - check all unique teams
            print("Available teams:", df['team'].unique()[:10])
        
        player_dict = dict(zip(canadiens['playerId'], canadiens['name']))
        
        print(f"✅ Found {len(player_dict)} Canadiens players:\n")
        for name in sorted(player_dict.values()):
            print(f"   - {name}")
        print()
        
        return list(player_dict.keys()), player_dict
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], {}

def download_player_data(player_id, player_name=None):
    """Download game-by-game data for a single player"""
    url = BASE_URL.format(player_id=player_id)
    filename = DATA_FOLDER / f"{player_id}.csv"
    
    # Skip if already downloaded and valid
    if filename.exists():
        try:
            df = pd.read_csv(filename)
            if len(df) > 0:
                return "skipped"
        except:
            pass
    
    try:
        response = requests.get(url, timeout=15)
        
        if response.status_code == 404:
            return "no_data"
        
        response.raise_for_status()
        
        if len(response.content) < 100:
            return "no_data"
        
        # Verify CSV
        try:
            df = pd.read_csv(pd.io.common.BytesIO(response.content))
            if len(df) == 0:
                return "no_data"
        except:
            return "invalid"
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        return "success"
        
    except requests.exceptions.Timeout:
        return "timeout"
    except requests.exceptions.RequestException:
        return "error"

def download_canadiens():
    """Download all Canadiens players"""
    
    player_ids, player_names = get_canadiens_players()
    
    if not player_ids:
        print("❌ No Canadiens players found!")
        print("\n💡 Trying to manually add known Canadiens players...")
        
        # Backup: manual list of key Canadiens players (2024-25)
        known_canadiens = {
            8481540: "Cole Caufield",
            8478398: "Nick Suzuki",
            8480830: "Juraj Slafkovsky",
            8481519: "Kaiden Guhle",
            8478507: "Jake Evans",
            8479325: "Joel Armia",
            8476885: "Brendan Gallagher",
            8475913: "David Savard",
            8476923: "Mike Matheson",
            8478469: "Christian Dvorak",
            8480038: "Jordan Harris",
            8481722: "Josh Anderson",
            # Add more as needed
        }
        player_ids = list(known_canadiens.keys())
        player_names = known_canadiens
        print(f"✅ Using {len(player_ids)} known Canadiens players\n")
    
    print(f"📥 Downloading data for {len(player_ids)} players...")
    print(f"📂 Saving to: {DATA_FOLDER.absolute()}\n")
    
    stats = {
        "success": 0,
        "skipped": 0,
        "no_data": 0,
        "timeout": 0,
        "invalid": 0,
        "error": 0
    }
    
    for i, player_id in enumerate(player_ids, 1):
        player_name = player_names.get(player_id, str(player_id))
        
        print(f"[{i}/{len(player_ids)}] {player_name:<30}", end=" ")
        
        result = download_player_data(player_id, player_name)
        stats[result] += 1
        
        status_icons = {
            "success": "✅",
            "skipped": "⏭️",
            "no_data": "⚠️",
            "timeout": "⏱️",
            "invalid": "❌",
            "error": "❌"
        }
        
        status_messages = {
            "success": "Téléchargé",
            "skipped": "Déjà existe",
            "no_data": "Pas de données",
            "timeout": "Timeout",
            "invalid": "Données invalides",
            "error": "Erreur"
        }
        
        print(f"{status_icons[result]} {status_messages[result]}")
        
        time.sleep(0.5)
    
    print(f"\n{'='*60}")
    print(f"📊 Résumé - Canadiens de Montréal:")
    print(f"{'='*60}")
    print(f"✅ Téléchargés avec succès:  {stats['success']}")
    print(f"⏭️  Déjà existants:          {stats['skipped']}")
    print(f"⚠️  Pas de données:          {stats['no_data']}")
    print(f"⏱️  Timeouts:                {stats['timeout']}")
    print(f"❌ Invalides/Erreurs:       {stats['invalid'] + stats['error']}")
    print(f"{'='*60}")
    print(f"📂 Fichiers: {DATA_FOLDER.absolute()}")
    print(f"📈 Total utilisables: {stats['success'] + stats['skipped']}")
    print(f"\n💡 Prochaine étape: python build_players_game_by_game.py")

if __name__ == "__main__":
    download_canadiens()