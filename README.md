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
├── data/                              # 📊 Centralized data folder
│   ├── brentford_2021_2026.csv        # Main dataset (single source of truth)
│   └── README.md                      # Data documentation
├── assistant_coach/                   # 🤖 AI Assistant Coach module
│   ├── app.py                         # Streamlit chat interface
│   ├── agent.py                       # Groq LLM agent setup
│   ├── tools.py                       # Custom tools (stats, injuries, weather, news)
│   ├── requirements.txt               # Dependencies for the AI coach
│   └── README.md                      # Detailed AI coach documentation
├── assistant_coach_langchain/         # 🤖 LangChain AI Assistant Coach
│   ├── app.py                         # Streamlit chat interface
│   ├── agent.py                       # LangChain ReAct agent
│   ├── tools.py                       # LangChain tools
│   ├── config.py                      # Configuration and prompts
│   ├── requirements.txt               # Dependencies
│   └── README.md                      # LangChain documentation
├── dashboard/                         # 📊 Dash Analytics Dashboard module
│   ├── app.py                         # Main Dash application (layouts + callbacks)
│   ├── requirements.txt               # Dependencies for the Dashboard
│   ├── README.md                      # Detailed Dashboard documentation
│   └── assets/                        # CSS styles for the dashboard
├── notebooks/                         # 📓 Jupyter Notebooks
│   └── Brentford_analytics.ipynb      # Exploratory analysis notebook
├── docs/                              # 📚 Documentation
│   └── PROJECT_ANALYSIS.md            # Technical analysis and data techniques
├── .env                               # Environment variables (not in git)
├── .env.example                       # Environment template
├── pyproject.toml                     # uv package manager configuration
└── .gitignore                         # Git ignore rules
```

---

## 🚀 Getting Started

The Dashboard and the AI Assistant Coach are built as independent modules. You can run one or both depending on what you want to explore.

### 1. Prerequisites

- **Python 3.12+** (check with `python3 --version`)
- **uv** — Fast Python package manager (replaces pip, poetry, etc.)

#### Install uv

If you don't have `uv` installed, install it using one of these methods:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Or using Homebrew (macOS):**
```bash
brew install uv
```

**Or using pip:**
```bash
pip install uv
```

Verify installation:
```bash
uv --version
```

### 2. Project Setup with uv

#### Option A: Quick Setup (Recommended)

```bash
# Clone or navigate to the project directory
cd top_eleven

# Initialize uv project (if not already done)
uv init

# Install all dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate
# On Windows use: .\.venv\Scripts\Activate.ps1
```

#### Option B: Manual Setup

```bash
# Create and activate virtual environment
uv venv .venv
source .venv/bin/activate
# On Windows use: .\.venv\Scripts\Activate.ps1

# Install dependencies from pyproject.toml
uv pip install -e .

# Or install specific module dependencies
uv pip install -r dashboard/requirements.txt
uv pip install -r assistant_coach/requirements.txt
```

### 3. Environment Configuration

Create a `.env` file in the project root with your API keys:

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your API keys
# REQUIRED:
GROQ_API_KEY=your_groq_api_key_here

# OPTIONAL (for enhanced features):
APIFOOTBALL_KEY=your_api_football_key_here
TAVILY_KEY=your_tavily_api_key_here
```

**Get API Keys:**
- **Groq** (required): https://console.groq.com (free tier available)
- **API-Football** (optional): https://api-sports.io (free tier available)
- **Tavily** (optional): https://tavily.com (free tier available)

### 4. Running the Interactive Dashboard

The dashboard provides a visual overview of team and player performance.

```bash
# Using uv run (recommended)
uv run python dashboard/app.py

# Or if virtual environment is activated
python dashboard/app.py
```

*Open **http://localhost:8050** in your browser.*

**Dashboard Features:**
- 🏟️ Team Overview — Season KPIs, results distribution, goals trends
- 👤 Player Profiling — Individual stats, radar charts, comparisons
- 📈 Season Stats — Match-by-match breakdown, top performers
- 📖 Project Overview — Dataset info and color guide

### 5. Running the AI Assistant Coach

The Assistant Coach uses Groq (llama-3.3-70b) for tactical analysis and requires the `.env` file configured.

```bash
# Using uv run (recommended)
uv run streamlit run assistant_coach/app.py

# Or if virtual environment is activated
streamlit run assistant_coach/app.py
```

*Open the Local URL provided by Streamlit (usually **http://localhost:8501**) in your browser.*

**AI Coach Features:**
- 🤖 Natural language queries about squad, form, and tactics
- 📋 Automatic starting 11 selection with tactical reasoning
- ⚡ Fatigue analysis and rest recommendations
- 🌦️ Weather-aware tactical adjustments
- 🔄 Real-time injury updates and news context

**Example Queries:**
- *"Pick the best starting 11 vs Arsenal away on Saturday"*
- *"Who needs rest this week?"*
- *"Compare Toney and Igor Thiago this season"*
- *"Who are our top performers in the last 5 matches?"*

### 6. Running the Jupyter Notebook

For exploratory data analysis:

```bash
# Install Jupyter kernel for the project
uv pip install ipykernel

# Start Jupyter
uv run jupyter notebook

# Or if virtual environment is activated
jupyter notebook
```

Then open `notebooks/Brentford_analytics.ipynb`

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

## 🛠️ Common Commands with uv

```bash
# Sync dependencies (install/update)
uv sync

# Add a new package
uv pip install package_name

# Remove a package
uv pip uninstall package_name

# Run a command in the virtual environment
uv run python script.py
uv run streamlit run app.py

# Activate virtual environment manually
source .venv/bin/activate          # macOS/Linux
.\.venv\Scripts\Activate.ps1       # Windows PowerShell

# Deactivate virtual environment
deactivate

# Update all dependencies
uv pip install --upgrade -r pyproject.toml

# Create a lock file for reproducibility
uv lock
```

---

## ❓ Troubleshooting

### Installation Issues

| Issue | Solution |
|-------|----------|
| **`uv: command not found`** | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| **`ModuleNotFoundError`** | Run `uv sync` to install all dependencies |
| **`Python 3.12+ required`** | Check Python version: `python3 --version`. Update if needed. |
| **Virtual env not activating** | Use `uv run` instead, or check activation command for your OS |

### Runtime Issues

| Issue | Solution |
|-------|----------|
| **CSV not found** | Ensure `brentford_2021_2026.csv` exists in `dashboard/` and `assistant_coach/` folders |
| **Port already in use** | Change port in code: `app.run(port=8051)` for Dash or `--server.port 8502` for Streamlit |
| **Missing API Keys** | Create `.env` file: `cp .env.example .env` and add your Groq API key |
| **`GROQ_API_KEY not found`** | Ensure `.env` file is in project root and contains `GROQ_API_KEY=your_key` |
| **Streamlit not starting** | Try: `uv run streamlit run assistant_coach/app.py --logger.level=debug` |

### API Issues

| Issue | Solution |
|-------|----------|
| **Rate limit errors** | The AI Coach automatically falls back to a smaller model. Wait a moment and retry. |
| **Injuries/News not loading** | These are optional. Add `APIFOOTBALL_KEY` and `TAVILY_KEY` to `.env` for full features. |
| **Weather data missing** | Open-Meteo is free and doesn't require a key. Check your internet connection. |

---

## 📚 Additional Resources

- **Project Analysis**: See `docs/PROJECT_ANALYSIS.md` for detailed technical documentation
- **Dashboard Docs**: See `dashboard/README.md` for dashboard-specific features
- **AI Coach Docs**: See `assistant_coach/README.md` for AI coach details
- **uv Documentation**: https://docs.astral.sh/uv/
- **Groq Console**: https://console.groq.com

---

## 🤝 Contributing

This is an academic project for the Data Analysis course (2025–2026). For questions or improvements, contact the project authors:
- Ahmed Chakcha
- Mohamed Ali Djemal

---

## 📄 License

This project is provided as-is for educational purposes.

---

For more detailed module-specific notes, refer to `dashboard/README.md` and `assistant_coach/README.md`.
