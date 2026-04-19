# 🐝 Brentford FC Analytics Dashboard

An interactive football analytics dashboard that explores **Brentford FC** performance across **5 seasons (2021/22 → 2025/26)** using match and player-level statistics.

Built with **Python**, **Dash**, **Plotly**, and **pandas**.

---

## 🎯 About the Project

This project analyzes Brentford FC's performance from the 2021/22 season through to 2025/26. The goal is to explore match results, team statistics, and player performance to understand how the club has evolved over recent seasons.

The project has three parts:

1. **Dashboard** — a multi-page interactive web app for exploring the data visually.
2. **Notebook** — a Jupyter notebook for exploratory data analysis and experimentation.
3. **AI Assistant Coach** — an LLM-powered Streamlit app acting as a professional football coach that can answer queries about Brentford's data.

**Students:** Ahmed Chakcha – Mohamed Ali Djemal  
**Course:** Data Analysis  
**Instructor:** Dr. Khalil Masmoudi  
**Academic Year:** 2025–2026

---

## 📁 Repository Structure

```
Top_eleven/
├── README.md                          # This file
├── assistant_coach/                   # AI Assistant Coach module
│   ├── app.py                         # Streamlit chat interface
│   ├── agent.py                       # LangChain agent and LLM setup
│   ├── tools.py                       # Custom tools for data and web search
│   ├── requirements.txt               # Dependencies for the AI coach
│   └── README.md                      # AI coach documentation
├── dashboard/
│   ├── app.py                         # Main Dash application (layouts + callbacks)
│   ├── requirements.txt               # Python dependencies
│   ├── brentford_2021_2026.csv        # Dataset (player-match level, 5 seasons)
│   ├── README.md                      # Detailed dashboard documentation
│   └── assets/
│       ├── brentford.css              # Global dark theme styles
│       └── dropdowns.css              # Dropdown styling overrides
└── notebooks/
    └── Brentford_analytics.ipynb      # Exploratory analysis notebook
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r dashboard/requirements.txt
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r dashboard\requirements.txt
```

### Running the Dashboard

```bash
python3 dashboard/app.py
```

Open **http://localhost:8050** in your browser.

To use a different port, change `port=8050` in the last line of `dashboard/app.py`.

### Running the AI Assistant Coach

The Assistant Coach runs on Streamlit and requires its own dependencies and an `.env` file with API keys (e.g., `GEMINI_API_KEY`, `TAVILY_API_KEY`).

```bash
python3 -m pip install -r assistant_coach/requirements.txt
streamlit run assistant_coach/app.py
```

Open the local URL provided by Streamlit in your browser.

---

## 📄 Dashboard Pages

The dashboard has **4 pages**, accessible from the sidebar. You can hide the sidebar with the **"Hide menu"** button and bring it back with the **☰** button.

### 1. 🏟️ Team Overview

High-level view of Brentford's performance. Filter by season or view all seasons at once.

- **KPIs:** Matches, Wins, Win Rate, Avg Goals For, Avg Goals Against, Clean Sheets
- **Results per Season:** Grouped bar chart of Wins, Draws, and Losses
- **Goals For vs Against:** Line chart comparing average goals scored and conceded
- **Home vs Away Win Rate:** Win percentage by venue
- **Possession by Result:** Box plots showing possession distribution for W/D/L

### 2. 👤 Player Profiling

Analyze individual players with optional head-to-head comparison.

- **Filters:** Season, Player, and an optional second player to compare
- **Player Cards:** Position, appearances, goals, assists, average rating
- **Performance Radar:** Per-90 percentile chart across 6 metrics (Shots, Key Passes, Tackles Won, Passes, Goals, Assists). Each metric shows where the player ranks compared to the rest of the squad. Hover for both the percentile and the raw per-90 value.
- **Rating per Season:** Line chart tracking average rating over time
- **Career Stats Table:** Averages for minutes, shots, key passes, tackles won

When you select a specific season, the player dropdowns automatically filter to show only players with data in that season.

### 3. 📊 Season Stats

Deep dive into a single season.

- **KPIs:** Played, Wins, Draws, Losses, Goals For, Goals Against, Clean Sheets, Win Rate
- **Cumulative Wins:** Area chart showing the running total of wins match by match
- **Goals Timeline:** Bar chart showing goals scored and conceded per match
- **Top Performers:** Top 5 players by combined Goals + Assists
- **Match Results:** Full sortable table with date, venue, competition, score, result, possession, and shots

### 4. 📖 Project Overview

Informational page with project context, dataset summary, dashboard guide, and color legend.

---

## 📂 Dataset

The dashboard uses `dashboard/brentford_2021_2026.csv`.

The data is at **player-match level** — each match has multiple rows, one per player. The dataset covers **208 matches**, **81 players**, and **5 seasons**.

### Required Columns

**Match-level:**
`match_id`, `date`, `season`, `venue`, `competition`, `result`, `goals_for`, `goals_against`, `possession`, `total_shots`, `shots_on_target`, `corners`, `fouls_committed`

**Player-level:**
`player_name`, `position`, `minutes_played`, `goals`, `assists`, `shots`, `key_passes`, `tackles_won`, `total_passes`, `rating`

The app automatically creates a `result_win` column from `result == 'W'`.

---

## 🎨 Color Guide

The dashboard uses a consistent color scheme throughout all charts:

- **Green** (`#22C55E`) — Wins and win rate
- **Gold** (`#FFCF00`) — Draws and highlights
- **Red** (`#D0021B`) — Losses and goals scored (Brentford's primary color)
- **Grey** (`#6B7280`) — Goals against and neutral elements

---

## 📓 Exploratory Notebook

A Jupyter notebook is available at `notebooks/Brentford_analytics.ipynb` for exploratory analysis and experimentation outside the dashboard.

To run it:

```bash
python3 -m pip install notebook
jupyter notebook notebooks/Brentford_analytics.ipynb
```

---

## ❓ Troubleshooting

- **`ModuleNotFoundError`** — Run `python3 -m pip install -r dashboard/requirements.txt`
- **CSV not found** — Make sure `dashboard/brentford_2021_2026.csv` exists. If you renamed it, update the filename in `dashboard/app.py`.
- **Port already in use** — Change `port=8050` to another port in `dashboard/app.py`.

---

For more detailed page-by-page usage notes, see `dashboard/README.md`.

---

## ✍️ Authors

- **Ahmed Chakcha**
- **Mohamed Ali Djemal**
