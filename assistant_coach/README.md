# 🐝 Brentford FC — Assistant Coach Agent

AI assistant coach powered by **Groq (llama-3.3-70b)**.
Picks the best starting 11 based on current season (25/26) data,
injuries, news and weather.

---

## Setup

### 1 — Place your CSV next to app.py
```
brentford_agent/
├── app.py
├── agent.py
├── tools.py
├── requirements.txt
└── brentford_2021_2026_clean.csv
```

### 2 — Create .env file
```
GROQ_API_KEY=your_key          # required — free at console.groq.com
APIFOOTBALL_KEY=your_key       # optional — free at api-sports.io
TAVILY_KEY=your_key            # optional — free at tavily.com
```

### 3 — Install
```bash
pip install -r requirements.txt
```

### 4 — Run
```bash
streamlit run app.py
```

### 5 — Open
```
http://localhost:8501
```

---

## How it works

```
Coach question
      ↓
Groq LLM makes a plan
      ↓
Calls tools in sequence:
  squad_overview → get_injuries → rank_position
  → fatigue_check → search_news → match_weather
      ↓
LLM reasons over all results
      ↓
Starting 11 + reasons + bench options
```

## Tools

| Tool | Data | Purpose |
|------|------|---------|
| squad_overview | CSV 25/26 | Full squad form + fatigue |
| player_form | CSV 25/26 | Last N match stats |
| fatigue_check | CSV 25/26 | Minutes last 3 games |
| rank_position | CSV 25/26 | Best player per position |
| compare_two | CSV 25/26 | Side-by-side comparison |
| get_injuries | API-Football | Unavailable players |
| search_news | Tavily | Latest news |
| match_weather | Open-Meteo | Match conditions (free) |

## Example questions
- "Pick the best starting 11 vs Arsenal away on Saturday"
- "Who needs rest this week?"
- "Compare Toney and Igor Thiago this season"
- "Who are our top performers in the last 5 matches?"
- "What is the weather impact for Saturday's match?"
