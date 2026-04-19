# 🐝 Brentford FC Analytics & AI Coach

A comprehensive football analytics project exploring **Brentford FC's** performance across **5 seasons (2021/22 → 2025/26)**. This project combines data visualization, exploratory data analysis, and advanced AI to provide deep insights into the club's matches, squad, and tactics.

---

## 🎯 About the Project

This project was built to understand how Brentford FC has evolved over recent seasons and to provide tools that a professional football manager or analyst would use. 

The project is divided into three main pillars:

1. **📊 Interactive Dashboard** — A multi-page web app built with Dash to explore match results, team statistics, and player performance visually.
2. **🤖 AI Assistant Coach** — An LLM-powered Streamlit app acting as a professional football coach, capable of answering natural language queries about Brentford's data, injuries, weather, and tactical decisions.
3. **📓 Exploratory Notebook** — A Jupyter notebook for deep-dive exploratory data analysis and statistical experimentation.

**Students:** Ahmed Chakcha – Mohamed Ali Djemal  
**Course:** Data Analysis  
**Instructor:** Dr. Khalil Masmoudi  
**Academic Year:** 2025–2026

---

## 📁 Repository Structure

```
Top_eleven/
├── README.md                          # This file
├── assistant_coach/                   # 🤖 AI Assistant Coach module
│   ├── app.py                         # Streamlit chat interface
│   ├── agent.py                       # LangChain agent and Groq LLM setup
│   ├── tools.py                       # Custom RAG tools (stats, injuries, weather, news)
│   ├── brentford_2021_2026.csv        # Dataset for the AI Coach
│   ├── requirements.txt               # Dependencies for the AI coach
│   └── README.md                      # Detailed AI coach documentation
├── dashboard/                         # 📊 Dash Analytics Dashboard module
│   ├── app.py                         # Main Dash application (layouts + callbacks)
│   ├── brentford_2021_2026.csv        # Dataset for the Dashboard
│   ├── requirements.txt               # Dependencies for the Dashboard
│   ├── README.md                      # Detailed Dashboard documentation
│   └── assets/                        # CSS styles for the dashboard
└── notebooks/                         # 📓 Jupyter Notebooks
    └── Brentford_analytics.ipynb      # Exploratory analysis notebook
```

---

## 🚀 Getting Started

The Dashboard and the AI Assistant Coach are built as independent modules. You can run one or both depending on what you want to explore.

### 1. Prerequisites
- Python 3.x
- pip

It is recommended to use a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
# On Windows use: .\.venv\Scripts\Activate.ps1
```

### 2. Running the Interactive Dashboard

The dashboard provides a visual overview of team and player performance.

```bash
python3 -m pip install -r dashboard/requirements.txt
python3 dashboard/app.py
```
*Open **http://localhost:8050** in your browser.*

### 3. Running the AI Assistant Coach

The Assistant Coach uses Groq (llama-3.3-70b) and requires an `.env` file with API keys (e.g., `GROQ_API_KEY`, and optionally `APIFOOTBALL_KEY`, `TAVILY_KEY`).

```bash
# Ensure you are in the project root
python3 -m pip install -r assistant_coach/requirements.txt
streamlit run assistant_coach/app.py
```
*Open the Local URL provided by Streamlit (usually **http://localhost:8501**) in your browser.*

---

## 📊 Dashboard Deep Dive

The dashboard has **4 pages**, accessible from the sidebar. 

- **🏟️ Team Overview:** High-level view of Brentford's performance. Includes KPIs, results per season, goals for vs against, and home vs away win rates.
- **👤 Player Profiling:** Analyze individual players with optional head-to-head comparison. Features player cards, performance radar charts, and career stats.
- **📈 Season Stats:** Deep dive into a single season. Includes cumulative wins, match-by-match goals timeline, top performers, and a full sortable results table.
- **📖 Project Overview:** Context, dataset summary, and dashboard guide.

### 🎨 Color Guide
- **Green** (`#22C55E`) — Wins and win rate
- **Gold** (`#FFCF00`) — Draws and highlights
- **Red** (`#D0021B`) — Losses and goals scored (Brentford's primary color)
- **Grey** (`#6B7280`) — Goals against and neutral elements

---

## 🤖 AI Assistant Coach Deep Dive

The AI Assistant Coach is designed to answer complex, tactical questions using real data, live APIs, and web search.

### How it works
When you ask a question (e.g., *"Pick the best starting 11 vs Arsenal"*):
1. The **Groq LLM** creates an execution plan.
2. It dynamically calls a sequence of **Tools**:
   - `squad_overview` / `player_form` / `fatigue_check` / `compare_two` (from local CSV data)
   - `get_injuries` (from API-Football)
   - `search_news` (via Tavily)
   - `match_weather` (via Open-Meteo)
3. The LLM reasons over the combined results and returns a structured tactical response.

### Example Queries
- *"Pick the best starting 11 vs Arsenal away on Saturday"*
- *"Who needs rest this week?"*
- *"Compare Toney and Igor Thiago this season"*
- *"Who are our top performers in the last 5 matches?"*

---

## 📂 The Dataset

Both modules rely on the `brentford_2021_2026.csv` dataset, which contains **player-match level data** covering **208 matches**, **81 players**, and **5 seasons**.

**Match-level Columns:** `match_id`, `date`, `season`, `venue`, `competition`, `result`, `goals_for`, `goals_against`, `possession`, `total_shots`, `shots_on_target`, `corners`, `fouls_committed`

**Player-level Columns:** `player_name`, `position`, `minutes_played`, `goals`, `assists`, `shots`, `key_passes`, `tackles_won`, `total_passes`, `rating`

---

## ❓ Troubleshooting

- **`ModuleNotFoundError`** — Ensure you installed the correct requirements file for the module you are trying to run (`dashboard/requirements.txt` or `assistant_coach/requirements.txt`).
- **CSV not found** — Ensure the dataset is present in the respective module's folder.
- **Port already in use** — For Dash, change `port=8050` in `dashboard/app.py`. For Streamlit, pass `--server.port 8502` when running.
- **Missing API Keys** — Ensure your `.env` file is properly configured in the project root or `.env` file when running the AI coach.

---

For more detailed module-specific notes, refer to `dashboard/README.md` and `assistant_coach/README.md`.
