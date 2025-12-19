import pandas as pd
import glob
import os

# Dossier contenant tes CSV
DATA_FOLDER = "data/*.csv"

dfs = []

for file in glob.glob(DATA_FOLDER):
    print("Chargement :", os.path.basename(file))
    df = pd.read_csv(file)

    # Garder seulement la situation "other" (ou 5v5 si tu préfères)
    df = df[df["situation"] == "other"]

    # Calcul du plus/minus
    df["plusMinus"] = df["OnIce_F_goals"] - df["OnIce_A_goals"]

    # Colonnes essentielles
    keep = [
        "playerId", "season", "name", "team",
        "I_F_points", "I_F_goals", "plusMinus"
    ]

    df = df[keep]
    dfs.append(df)

# Fusionner toutes les saisons
all_seasons = pd.concat(dfs, ignore_index=True)

# Sauvegarder
all_seasons.to_csv("all_seasons_clean.csv", index=False)

print("✅ Fichier créé : all_seasons_clean.csv")