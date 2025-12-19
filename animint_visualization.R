library(tidyverse)
library(animint2)

# Lire le dataset généré par Python
df <- read_csv("players_game_by_game.csv",
               show_col_types = FALSE)

# Choix d'un joueur par défaut
default_player <- "Nick Suzuki"

# Sous-ensemble pour le joueur par défaut
df_player <- df %>% 
  filter(name == default_player)

# Visualisation animint2
viz <- animint2(
  title = "NHL Game-by-Game Cumulative Stats (MoneyPuck)",

  # 1. Courbe cumulative (points) par saison, alignée sur gameNumber
  cumulative_plot = ggplot() +
    geom_line(aes(
      x = gameNumber,
      y = cum_points,
      color = factor(season),
      showSelected = season,
      clickSelects = season
    ), data = df_player, size = 1.2) +
    geom_point(aes(
      x = gameNumber,
      y = cum_points,
      showSelected = season,
      clickSelects = season
    ), data = df_player, size = 1.5) +
    scale_color_brewer(palette = "Set1") +
    labs(
      x = "Game number",
      y = "Cumulative points",
      color = "Season"
    ) +
    theme_minimal(),

  # 2. Sélecteur de saison (bar chart)
  season_selector = ggplot() +
    geom_bar(aes(
      x = factor(season),
      fill = factor(season),
      clickSelects = season
    ), data = df_player) +
    scale_fill_brewer(palette = "Set1") +
    labs(x = "Season", y = "Number of games") +
    theme_minimal(),

  # 3. Sélecteur de joueur (liste cliquable)
  player_selector = ggplot() +
    geom_text(aes(
      x = 1,
      y = name,
      label = name,
      clickSelects = name
    ), data = df %>% distinct(name)) +
    theme_void()
)

# Générer la sortie animint2 dans un dossier
animint2dir(viz, "animint_output")