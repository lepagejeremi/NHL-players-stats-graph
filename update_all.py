# update_all.py - Complete automated update pipeline
import subprocess
import sys

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} - Complete!\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed!")
        print(f"Error: {e}\n")
        return False

def main():
    print("🏒 NHL Stats Complete Update Pipeline")
    print("="*60)
    
    # Step 1: Download latest data from MoneyPuck
    if not run_command("python download_all_moneypuck_players.py", 
                      "Step 1: Downloading player data from MoneyPuck"):
        sys.exit(1)
    
    # Step 2: Process and combine all player files
    if not run_command("python build_players_game_by_game.py",
                      "Step 2: Processing and combining player data"):
        sys.exit(1)
    
    # Step 3: Rebuild R dashboard
    if not run_command("Rscript build_live_dashboard.R",
                      "Step 3: Rebuilding interactive dashboard"):
        sys.exit(1)
    
    print("="*60)
    print("🎉 ALL DONE!")
    print("📂 Open: animint_output/index.html")
    print("="*60)

if __name__ == "__main__":
    main()
