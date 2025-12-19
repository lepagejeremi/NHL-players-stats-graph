import pandas as pd
import glob

# Folder containing all player game-by-game CSVs
DATA_FOLDER = "data_gbg/*.csv"

dfs = []

for file in glob.glob(DATA_FOLDER):
    df = pd.read_csv(file)

    # --- Fix date format (YYYYMMDD) ---
    df["gameDate"] = pd.to_datetime(
        df["gameDate"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # --- Keep only ONE situation to avoid duplicates ---
    # Prefer "all" if available, otherwise fallback to "other"
    if "all" in df["situation"].unique():
        df = df[df["situation"] == "all"]
    else:
        df = df[df["situation"] == "other"]

    # --- Compute per-game plus/minus ---
    df["plusMinus"] = df["OnIce_F_goals"] - df["OnIce_A_goals"]

    # --- Keep only useful columns ---
    keep = [
        "playerId", "name", "season", "gameId", "gameDate",
        "I_F_points", "I_F_goals", "plusMinus"
    ]
    df = df[keep]

    # --- Group by match to avoid duplicates across situations ---
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

# --- Combine all players ---
all_games = pd.concat(dfs, ignore_index=True)

# --- Final sort ---
all_games = all_games.sort_values(["name", "season", "gameDate"])

# --- Save final dataset ---
all_games.to_csv("players_game_by_game.csv", index=False)

print("✅ players_game_by_game.csv created successfully!")