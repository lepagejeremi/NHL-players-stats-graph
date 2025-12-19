# build_live_dashboard.R - Dashboard with manual refresh capability
library(tidyverse)
library(jsonlite)

cat("🔄 Loading data from players_game_by_game.csv...\n")

# Load data
df <- read_csv("players_game_by_game.csv", show_col_types = FALSE)

# Prepare data for web
df <- df %>%
  rename(player = name) %>%
  mutate(
    season = as.character(season),
    gameDate = as.character(gameDate)
  )

# Create season summary
season_summary <- df %>%
  group_by(player, season) %>%
  summarise(
    GP = n(),
    G = sum(I_F_goals),
    A = sum(I_F_points) - sum(I_F_goals),
    P = sum(I_F_points),
    plusMinus = sum(plusMinus),
    PPG = round(sum(I_F_points) / n(), 2),
    .groups = "drop"
  )

# Get last update time
last_update <- format(Sys.time(), "%Y-%m-%d %H:%M:%S")
total_players <- length(unique(df$player))
total_games <- nrow(df)

cat("✅ Loaded", total_players, "players,", total_games, "total games\n")

# Convert to JSON
game_json <- toJSON(df, dataframe = "rows")
season_json <- toJSON(season_summary, dataframe = "rows")

# Create HTML with refresh capability
html_content <- paste0('
<!DOCTYPE html>
<html>
<head>
    <title>NHL Game-by-Game Stats - LIVE</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .update-info {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 20px;
            color: #666;
            font-size: 14px;
            flex-wrap: wrap;
        }
        .stats-badge {
            background: #e3f2fd;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 12px;
            color: #1976d2;
            font-weight: bold;
        }
        .refresh-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            transition: all 0.3s;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
        .refresh-btn:hover {
            background: #218838;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        }
        .refresh-btn:active {
            transform: translateY(0);
        }
        .status-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 5px;
            background: #28a745;
            box-shadow: 0 0 10px #28a745;
        }
        .container {
            display: grid;
            grid-template-columns: 250px 1fr;
            gap: 20px;
            max-width: 1800px;
            margin: 0 auto;
        }
        .right-column {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .panel {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h2 {
            margin-top: 0;
            color: #555;
            font-size: 18px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        select {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            border: 2px solid #ddd;
            border-radius: 4px;
            margin-bottom: 10px;
            cursor: pointer;
        }
        select:focus {
            outline: none;
            border-color: #007bff;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th {
            background: #007bff;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: bold;
            position: sticky;
            top: 0;
        }
        td {
            padding: 8px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f8f9fa;
        }
        #plot {
            height: 500px;
        }
        .search-box {
            margin-bottom: 15px;
        }
        .search-box input {
            width: 100%;
            padding: 10px;
            font-size: 14px;
            border: 2px solid #ddd;
            border-radius: 4px;
        }
        .search-box input:focus {
            outline: none;
            border-color: #007bff;
        }
        .player-count {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        .left-column {
            height: fit-content;
            position: sticky;
            top: 20px;
        }
        .refresh-instructions {
            background: #fff3cd;
            border: 1px solid #ffc107;
            border-radius: 5px;
            padding: 15px;
            margin-top: 10px;
            font-size: 13px;
        }
        .refresh-instructions strong {
            display: block;
            margin-bottom: 5px;
            color: #856404;
        }
        .refresh-instructions ol {
            margin: 5px 0;
            padding-left: 20px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏒 NHL Game-by-Game Statistics</h1>
        <div class="update-info">
            <span class="stats-badge">👥 ', total_players, ' Players</span>
            <span class="stats-badge">🎮 ', format(total_games, big.mark=","), ' Games</span>
            <span>
                <span class="status-indicator"></span>
                Last updated: <strong id="lastUpdate">', last_update, '</strong>
            </span>
            <button class="refresh-btn" onclick="showRefreshInstructions()">
                🔄 Update Data
            </button>
        </div>
        
        <div class="refresh-instructions" id="refreshInstructions" style="display: none; max-width: 600px; margin: 20px auto 0;">
            <strong>📝 To update with latest stats:</strong>
            <ol>
                <li>Download latest CSV files from MoneyPuck to <code>data_gbg/</code></li>
                <li>Run: <code>python build_players_game_by_game.py</code></li>
                <li>Run: <code>Rscript build_live_dashboard.R</code></li>
                <li>Refresh this page in your browser (F5)</li>
            </ol>
        </div>
    </div>
    
    <div class="container">
        <div class="left-column">
            <div class="panel">
                <h2>Select Player</h2>
                <div class="search-box">
                    <input type="text" id="searchBox" placeholder="Search players..." />
                </div>
                <select id="playerSelect" size="30"></select>
                <div class="player-count" id="playerCount"></div>
            </div>
        </div>
        
        <div class="right-column">
            <div class="panel">
                <h2>Season Statistics</h2>
                <div id="statsTable"></div>
            </div>
            
            <div class="panel">
                <div id="plot"></div>
            </div>
        </div>
    </div>

    <script>
        // Embedded data
        let gameData = ', game_json, ';
        let seasonData = ', season_json, ';
        
        let allPlayers = [];
        let currentPlayer = null;

        function init() {
            allPlayers = [...new Set(gameData.map(g => g.player))].sort();
            console.log("✅ Loaded", allPlayers.length, "players");
            
            updatePlayerList(allPlayers);
            
            // Auto-select first player
            if (allPlayers.length > 0) {
                selectPlayer(allPlayers[0]);
            }
        }

        function updatePlayerList(players) {
            const select = document.getElementById("playerSelect");
            select.innerHTML = "";
            
            players.forEach(player => {
                const option = document.createElement("option");
                option.value = player;
                option.textContent = player;
                select.appendChild(option);
            });
            
            document.getElementById("playerCount").textContent = 
                `${players.length} player${players.length !== 1 ? "s" : ""}`;
        }

        document.getElementById("searchBox").addEventListener("input", (e) => {
            const search = e.target.value.toLowerCase();
            const filtered = allPlayers.filter(p => 
                p.toLowerCase().includes(search)
            );
            updatePlayerList(filtered);
            
            if (filtered.length > 0) {
                document.getElementById("playerSelect").value = filtered[0];
            }
        });

        document.getElementById("playerSelect").addEventListener("change", (e) => {
            selectPlayer(e.target.value);
        });

        function selectPlayer(playerName) {
            currentPlayer = playerName;
            
            const playerGames = gameData.filter(g => g.player === playerName);
            const playerSeasons = seasonData.filter(s => s.player === playerName);
            
            updateStatsTable(playerSeasons);
            
            const seasons = [...new Set(playerGames.map(g => g.season))].sort();
            const traces = seasons.map(season => {
                const seasonGames = playerGames.filter(g => g.season === season);
                
                return {
                    x: seasonGames.map(g => g.gameNumber),
                    y: seasonGames.map(g => g.cum_points),
                    mode: "lines+markers",
                    name: season,
                    line: { width: 2 },
                    marker: { size: 6 },
                    text: seasonGames.map(g => 
                        `<b>Game ${g.gameNumber}</b><br>` +
                        `Date: ${g.gameDate}<br>` +
                        `─────────────<br>` +
                        `Points: ${g.I_F_points}<br>` +
                        `Goals: ${g.I_F_goals}<br>` +
                        `+/-: ${g.plusMinus >= 0 ? "+" : ""}${g.plusMinus}<br>` +
                        `─────────────<br>` +
                        `Cumulative: <b>${g.cum_points}</b> pts`
                    ),
                    hovertemplate: "%{text}<extra></extra>"
                };
            });
            
            const layout = {
                title: {
                    text: `${playerName} - Cumulative Points by Game`,
                    font: { size: 18, weight: "bold" }
                },
                xaxis: { 
                    title: "Game Number",
                    gridcolor: "#f0f0f0"
                },
                yaxis: { 
                    title: "Cumulative Points",
                    gridcolor: "#f0f0f0"
                },
                hovermode: "closest",
                showlegend: true,
                legend: { 
                    orientation: "h", 
                    y: -0.15,
                    x: 0.5,
                    xanchor: "center"
                },
                plot_bgcolor: "#fafafa",
                paper_bgcolor: "white"
            };
            
            Plotly.newPlot("plot", traces, layout, {responsive: true});
        }

        function updateStatsTable(seasons) {
            const sorted = seasons.sort((a, b) => b.season - a.season);
            
            let html = `
                <table>
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>GP</th>
                            <th>G</th>
                            <th>A</th>
                            <th>P</th>
                            <th>+/-</th>
                            <th>PPG</th>
                        </tr>
                    </thead>
                    <tbody>
            `;
            
            sorted.forEach(s => {
                html += `
                    <tr>
                        <td><strong>${s.season}</strong></td>
                        <td>${s.GP}</td>
                        <td>${s.G}</td>
                        <td>${s.A}</td>
                        <td><strong>${s.P}</strong></td>
                        <td>${s.plusMinus >= 0 ? "+" : ""}${s.plusMinus}</td>
                        <td>${s.PPG}</td>
                    </tr>
                `;
            });
            
            // Career totals
            const totals = {
                GP: sorted.reduce((sum, s) => sum + s.GP, 0),
                G: sorted.reduce((sum, s) => sum + s.G, 0),
                A: sorted.reduce((sum, s) => sum + s.A, 0),
                P: sorted.reduce((sum, s) => sum + s.P, 0),
                plusMinus: sorted.reduce((sum, s) => sum + s.plusMinus, 0)
            };
            totals.PPG = (totals.P / totals.GP).toFixed(2);
            
            html += `
                    <tr style="background: #e3f2fd; font-weight: bold;">
                        <td>CAREER</td>
                        <td>${totals.GP}</td>
                        <td>${totals.G}</td>
                        <td>${totals.A}</td>
                        <td>${totals.P}</td>
                        <td>${totals.plusMinus >= 0 ? "+" : ""}${totals.plusMinus}</td>
                        <td>${totals.PPG}</td>
                    </tr>
                </tbody>
            </table>
            `;
            
            document.getElementById("statsTable").innerHTML = html;
        }

        function showRefreshInstructions() {
            const instructions = document.getElementById("refreshInstructions");
            instructions.style.display = instructions.style.display === "none" ? "block" : "none";
        }

        // Initialize
        init();
    </script>
</body>
</html>
')

# Write HTML file
writeLines(html_content, "animint_output/index.html")

cat("\n✅ Dashboard created successfully!\n")
cat("📂 Open: animint_output/index.html\n")
cat("\n💡 To update with latest stats:\n")
cat("   1. Download latest MoneyPuck CSVs to data_gbg/\n")
cat("   2. Run: python build_players_game_by_game.py\n")
cat("   3. Run: Rscript build_live_dashboard.R\n")
cat("   4. Refresh browser (F5)\n")