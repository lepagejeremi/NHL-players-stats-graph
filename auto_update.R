# auto_update.R - Automatically update data every X minutes
library(tidyverse)

cat("🔄 NHL Stats Auto-Updater Started\n")
cat("⏰ Will check for updates every 30 minutes\n")
cat("Press Ctrl+C to stop\n\n")

update_dashboard <- function() {
  timestamp <- format(Sys.time(), "%Y-%m-%d %H:%M:%S")
  cat("─────────────────────────────────────────\n")
  cat("⏰", timestamp, "\n")
  
  # Step 1: Run Python script to process data
  cat("1️⃣  Running Python data processing...\n")
  result <- system("python build_players_game_by_game.py", intern = TRUE)
  cat(paste(result, collapse = "\n"), "\n")
  
  # Step 2: Rebuild HTML dashboard
  cat("2️⃣  Rebuilding dashboard...\n")
  source("build_live_dashboard.R")
  
  cat("✅ Update complete!\n\n")
}

# Run immediately on start
update_dashboard()

# Then run every 30 minutes
while(TRUE) {
  Sys.sleep(30 * 60)  # 30 minutes
  update_dashboard()
}