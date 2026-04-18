# Brentford FC Analytics Dashboard (Dash)

An interactive multi-page dashboard built with **Dash + Plotly + pandas** to analyze Brentford FC performance from **2021/22 → 2025/26** using match- and player-level statistics.

## What’s inside

- **Team Overview**: season KPIs + results distribution, goals trends, home/away win-rate, and possession by result.
- **Player Profiling**: season-filtered player selection, player cards, comparison, performance radar, rating trend, and summary table.
- **Season Stats**: single-season deep dive with KPIs, cumulative wins, goals timeline, top performers, and match results table.
- **Project Overview**: short explanation of the dataset, how to use the dashboard, and the color guide.

## Project structure

This repository is organized so that everything needed to run the dashboard lives under the `dashboard/` folder:

```
dashboard/
	app.py
	requirements.txt
	brentford_2021_2026.csv
	assets/
		brentford.css
		dropdowns.css
```

Dash automatically loads CSS from the `assets/` folder.

## Requirements

- Python 3.x
- `pip` (or `python3 -m pip`)

## Installation

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r dashboard/requirements.txt
```

If you already have a virtual environment, activate it and run only the last line.

## Run the dashboard

Option A (recommended, from repository root):

```bash
python3 dashboard/app.py
```

Option B (from inside the folder):

```bash
cd dashboard
python3 app.py
```

Then open:

- http://localhost:8050

## How to use the dashboard

### Navigation

- Use the **sidebar** to switch pages.
- Click **Hide menu** to collapse the sidebar.
- When hidden, click the floating **☰** button to show it again.

### Team Overview ("/")

**Filter**
- Season: `All Seasons` or one season (21/22 → 25/26)

**KPIs**
- Matches, Wins, Win Rate, Avg Goals For, Avg Goals Against, Clean Sheets

**Charts**
- **Results per Season**: grouped bars for Win/Draw/Loss.
- **Goals For vs Against**: season averages (two lines).
- **Home vs Away Win Rate**: win percentage by venue.
- **Possession by Result**: distribution (box plots) for W/D/L.

### Player Profiling ("/player")

**Filters**
- **Season**: `All Seasons` or a single season
- **Player**: main player
- **Compare With**: optional second player (or `None`)

Important: when you select a **specific season** (example: **25/26**), the Player and Compare dropdowns are **automatically filtered** to show **only players who have data in that season**.

**Player cards**
- Apps, Goals, Assists, Avg Rating (+ position)

**Performance radar (per 90 · percentile)**
- Metrics: Shots · Key Passes · Tackles Won · Passes · Goals · Assists
- Each axis shows the player’s **percentile (0–100)** for the selected season, based on **per‑90** values.
- Hover shows both: **percentile** and the underlying **per‑90** number.

**Rating per Season**
- Line chart showing average rating by season (for the selected player(s)).

**Career stats table**
- Compact table of the main per-match averages shown in the cards.

### Season Stats ("/season")

**Filter**
- Season (single selection)

**KPIs**
- Played, Wins/Draws/Losses, Goals For/Against, Clean Sheets, Win Rate

**Charts**
- **Cumulative Wins**: season running total.
- **Goals Timeline**: match-by-match goals for vs goals against.

**Tables**
- **Top performers**: top 5 by Goals+Assists (with appearances and rating).
- **Match results**: sortable table with score, result, possession, shots.

### Project Overview ("/project")

- Explains what the dashboard contains, the dataset summary, and the color guide.

## Color guide

- **Green**: wins / win-rate
- **Gold**: draws / highlights
- **Red**: losses
- **Grey / Dark**: goals against / neutral UI

## Dataset

### Data file

The dashboard uses:

- `dashboard/brentford_2021_2026.csv`

The dataset is expected to be at **player-match level** (a match appears multiple times — one row per player).

### Required columns (used by the app)

At minimum, these columns must exist:

- Match-level: `match_id`, `date`, `season`, `venue`, `competition`, `result`, `goals_for`, `goals_against`, `possession`, `total_shots`, `shots_on_target`, `corners`, `fouls_committed`
- Player-level: `player_name`, `position`, `minutes_played`, `goals`, `assists`, `shots`, `key_passes`, `tackles_won`, `total_passes`, `rating`

Note: the app derives `result_win` automatically from `result == 'W'`.

## Troubleshooting

- **`ModuleNotFoundError` (dash / pandas / plotly)**
	- Run: `python3 -m pip install -r dashboard/requirements.txt`

- **CSV not found / wrong file name**
	- Ensure `dashboard/brentford_2021_2026.csv` exists.
	- If you want to use a different filename, update the CSV filename in `dashboard/app.py`.

- **Port already in use**
	- Edit the last line of `dashboard/app.py` and change `port=8050` to another port.

## Data source

Dataset source (as referenced in the dashboard):

- Kaggle: https://kaggle.com/datasets/543718cc009af71cc9dc369fb12aa33f8c5369747315f1ccece2749811839f2a
