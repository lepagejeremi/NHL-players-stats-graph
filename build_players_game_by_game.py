import pandas as pd
import glob

# Folder containing all player game-by-game CSVs
DATA_FOLDER = "data_gbg/*.csv"

print("🔍 Scanning for CSV files...")
files = glob.glob(DATA_FOLDER)
print(f"✅ Found {len(files)} CSV files in data_gbg/\n")

if len(files) == 0:
    print("❌ No CSV files found!")
    exit(1)

dfs = []
errors = []

for i, file in enumerate(files, 1):
    try:
        print(f"[{i}/{len(files)}] Processing: {file}...", end=" ")
        
        df = pd.read_csv(file)
        
        # Check if file has data
        if len(df) == 0:
            print("⚠️  Empty file, skipping")
            continue
        
        # Check required columns
        required_cols = ['playerId', 'name', 'season', 'gameId', 'gameDate', 'situation']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"⚠️  Missing columns: {missing}, skipping")
            errors.append((file, f"Missing columns: {missing}"))
            continue

        # --- Fix date format (YYYYMMDD) ---
        df["gameDate"] = pd.to_datetime(
            df["gameDate"].astype(str),
            format="%Y%m%d",
            errors="coerce"
        )

        # --- Keep only ONE situation to avoid duplicates ---
        if "all" in df["situation"].unique():
            df = df[df["situation"] == "all"]
        else:
            df = df[df["situation"] == "other"]

        # --- Compute per-game plus/minus ---
        if "OnIce_F_goals" in df.columns and "OnIce_A_goals" in df.columns:
            df["plusMinus"] = df["OnIce_F_goals"] - df["OnIce_A_goals"]
        else:
            df["plusMinus"] = 0

        # --- Keep only useful columns ---
        keep = [
            "playerId", "name", "season", "gameId", "gameDate",
            "I_F_points", "I_F_goals", "plusMinus"
        ]
        
        # Check if required stats columns exist
        if "I_F_points" not in df.columns or "I_F_goals" not in df.columns:
            print(f"⚠️  Missing stats columns, skipping")
            errors.append((file, "Missing I_F_points or I_F_goals"))
            continue
        
        df = df[keep]

        # --- Group by match to avoid duplicates ---
        df = df.groupby(
            ["playerId", "name", "season", "gameId", "gameDate"],
            as_index=False
        ).agg({
            "I_F_points": "sum",
            "I_F_goals": "sum",
            "plusMinus": "sum"
        })

        # --- Sort games correctly ---
        df = df.sort_values(["season", "gameDate"])

        # --- Add game number (1, 2, 3...) per season ---
        df["gameNumber"] = df.groupby(["playerId", "season"]).cumcount() + 1

        # --- Add cumulative stats ---
        df["cum_points"] = df.groupby(["playerId", "season"])["I_F_points"].cumsum()
        df["cum_goals"] = df.groupby(["playerId", "season"])["I_F_goals"].cumsum()
        df["cum_plusMinus"] = df.groupby(["playerId", "season"])["plusMinus"].cumsum()

        dfs.append(df)
        player_name = df['name'].iloc[0]
        print(f"✅ {player_name} ({len(df)} games)")

    except Exception as e:
        print(f"❌ Error: {e}")
        errors.append((file, str(e)))

print(f"\n{'='*60}")
print(f"📊 Processing Summary:")
print(f"{'='*60}")
print(f"✅ Successfully processed: {len(dfs)} players")
print(f"❌ Errors: {len(errors)}")

if errors:
    print(f"\n⚠️  Files with errors:")
    for file, error in errors:
        print(f"   - {file}: {error}")

if len(dfs) == 0:
    print("\n❌ No data to combine! Check the errors above.")
    exit(1)

# --- Combine all players ---
print(f"\n🔄 Combining all players...")
all_games = pd.concat(dfs, ignore_index=True)

# --- Final sort ---
all_games = all_games.sort_values(["name", "season", "gameDate"])

print(f"✅ Combined {len(all_games)} total games")
print(f"✅ {all_games['name'].nunique()} unique players:")
for player in sorted(all_games['name'].unique()):
    player_games = len(all_games[all_games['name'] == player])
    print(f"   - {player}: {player_games} games")

# --- Save final dataset ---
all_games.to_csv("players_game_by_game.csv", index=False)

print(f"\n{'='*60}")
print(f"✅ players_game_by_game.csv created successfully!")
print(f"📂 {len(all_games)} rows, {all_games['name'].nunique()} players")
print(f"{'='*60}")
