import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("players_game_by_game.csv")

st.title("NHL – Cumulative Game-by-Game Comparison")

player = st.selectbox(
    "Choisir un joueur",
    sorted(df["name"].unique())
)

stat = st.selectbox(
    "Statistique cumulative",
    ["cum_points", "cum_goals", "cum_plusMinus"]
)

# Filtrer pour un seul joueur
player_df = df[df["name"] == player]

# Choisir les saisons à superposer
seasons = st.multiselect(
    "Choisir les saisons à comparer",
    sorted(player_df["season"].unique()),
    default=sorted(player_df["season"].unique())
)

filtered = player_df[player_df["season"].isin(seasons)]

fig = px.line(
    filtered,
    x="gameNumber",
    y=stat,
    color="season",
    markers=True,
    title=f"{player} – {stat} (comparaison par saison)"
)

st.plotly_chart(fig, use_container_width=True)