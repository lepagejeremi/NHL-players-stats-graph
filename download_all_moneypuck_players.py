# download_all_moneypuck_players.py - CORRECT URL PATH
import requests
import pandas as pd
import time
from pathlib import Path

DATA_FOLDER = Path("data_gbg")
DATA_FOLDER.mkdir(exist_ok=True)

# CORRECTED URL - with /regular/skaters/
BASE_URL = "https://moneypuck.com/moneypuck/playerData/careers/gameByGame/regular/skaters/{player_id}.csv"

def get_multi_season_players():
    """Get players from multiple seasons (more comprehensive)"""
    print("📋 Fetching players from multiple seasons...\n")
    
    all_players = {}
    seasons = [2024, 2023, 2022, 2021, 2020, 2019]  # Last 6 seasons
    
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
        
        # Handle 404 gracefully
        if response.status_code == 404:
            return "no_data"
        
        response.raise_for_status()
        
        # Check if file has content
        if len(response.content) < 100:
            return "no_data"
        
        # Verify it's valid CSV
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
    except requests.exceptions.RequestException as e:
        return "error"

def download_all(max_players=None):
    """
    Main function to download all player data
    max_players: Limit number of players (useful for testing)
    """
    
    player_ids, player_names = get_multi_season_players()
    
    if not player_ids:
        print("❌ No players found!")
        return
    
    # Limit if specified
    if max_players:
        player_ids = player_ids[:max_players]
        print(f"⚠️  Limited to first {max_players} players for testing\n")
    
    print(f"📥 Starting download for {len(player_ids)} players...")
    print(f"📂 Saving to: {DATA_FOLDER.absolute()}\n")
    
    # Counters
    stats = {
        "success": 0,
        "skipped": 0,
        "no_data": 0,
        "timeout": 0,
        "invalid": 0,
        "error": 0
    }
    
    # Safety: stop after too many consecutive failures
    max_consecutive_fails = 20
    consecutive_fails = 0
    
    for i, player_id in enumerate(player_ids, 1):
        player_name = player_names.get(player_id, str(player_id))
        
        # Progress indicator
        print(f"[{i}/{len(player_ids)}] {player_name:<35}", end=" ")
        
        result = download_player_data(player_id, player_name)
        stats[result] += 1
        
        # Check for too many failures
        if result in ["timeout", "error"]:
            consecutive_fails += 1
            if consecutive_fails >= max_consecutive_fails:
                print(f"\n\n⚠️  {max_consecutive_fails} échecs consécutifs. Arrêt de sécurité.")
                break
        else:
            consecutive_fails = 0
        
        # Status messages
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
        
        # Rate limiting
        if result in ["success", "error", "timeout"]:
            time.sleep(0.5)
        else:
            time.sleep(0.1)
    
    # Summary
    print(f"\n{'='*70}")
    print(f"📊 Résumé du téléchargement:")
    print(f"{'='*70}")
    print(f"✅ Téléchargés avec succès:  {stats['success']}")
    print(f"⏭️  Déjà existants:          {stats['skipped']}")
    print(f"⚠️  Pas de données:          {stats['no_data']}")
    print(f"⏱️  Timeouts:                {stats['timeout']}")
    print(f"❌ Invalides/Erreurs:       {stats['invalid'] + stats['error']}")
    print(f"{'='*70}")
    print(f"📂 Fichiers sauvegardés: {DATA_FOLDER.absolute()}")
    print(f"📈 Total fichiers utilisables: {stats['success'] + stats['skipped']}")
    print(f"\n💡 Prochaine étape: python build_players_game_by_game.py")

if __name__ == "__main__":
    # Pour tester: télécharger seulement 50 joueurs
    # download_all(max_players=50)
    
    # Pour tout télécharger:
    download_all()