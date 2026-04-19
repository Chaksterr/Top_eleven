"""
tools.py
All data tools for the Brentford Assistant Coach.
Local  → your CSV (season 25/26 only)
External → API-Football (injuries), Tavily (news), Open-Meteo (weather)
"""

import os, json, requests
import pandas as pd

# ── Load current season only ──────────────────────────────────────────────────
for path in [
    "brentford_2021_2026.csv",
    "brentford_agent2/brentford_2021_2026.csv",
    "/content/sample_data/brentford_2021_2026.csv"
]:
    if os.path.exists(path):
        _raw = pd.read_csv(path)
        break

SEASON = "25/26"
df     = _raw[_raw["season"] == SEASON].copy()

# Tactical profile — edit this to match the coach's system
PROFILE = {
    "formation":  "4-3-3",
    "style":      "high_press",
    "fatigue_threshold": 240,          # minutes in last 3 games = rest needed
    "position_priorities": {
        "F": ["goals", "shots", "assists", "rating"],
        "M": ["tackles_won", "key_passes", "accurate_passes", "rating"],
        "D": ["clearances", "interceptions", "aerial_duels_won", "rating"],
        "G": ["rating", "saves"]
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# LOCAL TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def player_form(player_name: str, last_n: int = 5) -> dict:
    """Last N match stats for a player in current season."""
    p = df[df["player_name"].str.lower() == player_name.lower()]
    if p.empty:
        return {"error": f"'{player_name}' not found in season {SEASON}"}
    last = p.sort_values("date").tail(last_n)
    return {
        "player":          player_name,
        "matches_analysed": len(last),
        "avg_rating":      round(last["rating"].mean(), 2),
        "rating_trend":    [round(r, 2) for r in last["rating"].tolist()],
        "goals":           int(last["goals"].sum()),
        "assists":         int(last["assists"].sum()),
        "avg_shots":       round(last["shots"].mean(), 2),
        "avg_minutes":     round(last["minutes_played"].mean(), 1),
        "avg_key_passes":  round(last["key_passes"].mean(), 2),
        "avg_tackles_won": round(last["tackles_won"].mean(), 2),
        "position":        p["position"].iloc[0]
    }


def fatigue_check(player_name: str) -> dict:
    """Check if a player is fatigued (minutes in last 3 matches)."""
    p = df[df["player_name"].str.lower() == player_name.lower()]
    if p.empty:
        return {"error": f"'{player_name}' not found"}
    last3     = p.sort_values("date").tail(3)
    total_min = round(last3["minutes_played"].sum(), 0)
    threshold = PROFILE["fatigue_threshold"]
    return {
        "player":          player_name,
        "minutes_last_3":  total_min,
        "threshold":       threshold,
        "fatigued":        total_min >= threshold,
        "risk":            "HIGH ⚠️" if total_min >= threshold else "LOW ✅"
    }


def rank_position(position: str) -> dict:
    """Rank all players at a position by tactical fit and current season form."""
    pos_df = df[df["position"] == position.upper()]
    if pos_df.empty:
        return {"error": f"No players for position '{position}'"}

    cols = PROFILE["position_priorities"].get(position.upper(), ["rating"])
    # Only use columns that actually exist in the data
    cols = [c for c in cols if c in pos_df.columns]
    if not cols:
        cols = ["rating"]

    agg  = pos_df.groupby("player_name")[cols + ["minutes_played"]].mean().reset_index()

    for c in cols:
        mn, mx   = agg[c].min(), agg[c].max()
        agg[c+"_n"] = (agg[c] - mn) / (mx - mn + 1e-9)

    agg["score"] = agg[[c+"_n" for c in cols]].mean(axis=1).round(3)
    ranked = (agg.sort_values("score", ascending=False)
                 [["player_name","score"] + cols]
                 .head(6))
    return {
        "position": position.upper(),
        "players":  ranked.to_dict(orient="records")
    }


def squad_overview() -> dict:
    """Full squad — position, form rating, fatigue for current season."""
    result = []
    for p in df["player_name"].unique():
        pdata = df[df["player_name"] == p]
        f     = fatigue_check(p)
        result.append({
            "player":     p,
            "position":   pdata["position"].iloc[0],
            "apps":       len(pdata),
            "avg_rating": round(pdata["rating"].mean(), 2),
            "goals":      int(pdata["goals"].sum()),
            "assists":    int(pdata["assists"].sum()),
            "fatigued":   f.get("fatigued", False)
        })
    return {"squad": sorted(result, key=lambda x: x["avg_rating"], reverse=True)}


def compare_two(player1: str, player2: str) -> dict:
    """Side-by-side comparison of two players this season."""
    def s(name):
        p = df[df["player_name"].str.lower() == name.lower()]
        if p.empty: return {"error": f"'{name}' not found"}
        return {
            "player":      name,
            "position":    p["position"].iloc[0],
            "apps":        len(p),
            "avg_rating":  round(p["rating"].mean(), 2),
            "goals":       int(p["goals"].sum()),
            "assists":     int(p["assists"].sum()),
            "avg_shots":   round(p["shots"].mean(), 2),
            "avg_key_passes": round(p["key_passes"].mean(), 2),
            "avg_tackles_won": round(p["tackles_won"].mean(), 2),
            "avg_minutes": round(p["minutes_played"].mean(), 1)
        }
    return {"player1": s(player1), "player2": s(player2)}


# ─────────────────────────────────────────────────────────────────────────────
# EXTERNAL TOOLS
# ─────────────────────────────────────────────────────────────────────────────

def get_injuries() -> dict:
    """Fetch Brentford injury list from API-Football (team_id=55)."""
    key = os.getenv("APIFOOTBALL_KEY", "") or os.getenv("FOOTBALLDATA_KEY", "")
    if not key:
        return {"injuries": [], "note": "Add APIFOOTBALL_KEY or FOOTBALLDATA_KEY to .env for live injuries"}
    try:
        r = requests.get(
            "https://v3.football.api-sports.io/injuries",
            headers={"x-apisports-key": key},
            params={"team": 55, "season": 2025}, timeout=8
        )
        data = r.json().get("response", [])
        return {"injuries": [
            {"player": i["player"]["name"],
             "reason": i["player"].get("reason", "unknown")}
            for i in data
        ]}
    except Exception as e:
        return {"injuries": [], "error": str(e)}


def search_news(query: str) -> dict:
    """Search latest Brentford news via Tavily."""
    key = os.getenv("TAVILY_KEY", "")
    if not key:
        return {"results": [], "note": "Add TAVILY_KEY to .env for live news"}
    try:
        from tavily import TavilyClient
        res = TavilyClient(api_key=key).search(
            f"Brentford FC {query} 2025", max_results=3)
        return {"results": [
            {"title": r["title"], "summary": r["content"][:250]}
            for r in res.get("results", [])
        ]}
    except Exception as e:
        return {"results": [], "error": str(e)}


def match_weather(match_date: str) -> dict:
    """Match day weather at Brentford Community Stadium (free, no key needed)."""
    try:
        r = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 51.4882, "longitude": -0.3088,
                "daily": "precipitation_sum,windspeed_10m_max,temperature_2m_max",
                "timezone": "Europe/London",
                "start_date": match_date, "end_date": match_date
            }, timeout=8
        ).json()
        d = r.get("daily", {})
        rain = (d.get("precipitation_sum") or [0])[0] or 0
        wind = (d.get("windspeed_10m_max")  or [0])[0] or 0
        temp = (d.get("temperature_2m_max") or [0])[0] or 0
        return {
            "date": match_date,
            "temperature_c": temp,
            "wind_kmh": wind,
            "rain_mm":  rain,
            "impact":   "rainy — expect less possession play" if rain > 2
                        else "windy — long balls less effective" if wind > 30
                        else "good conditions"
        }
    except Exception as e:
        return {"error": str(e)}


# ── Tool registry (used by agent) ─────────────────────────────────────────────
TOOL_MAP = {
    "player_form":   player_form,
    "fatigue_check": fatigue_check,
    "rank_position": rank_position,
    "squad_overview": squad_overview,
    "compare_two":   compare_two,
    "get_injuries":  get_injuries,
    "search_news":   search_news,
    "match_weather": match_weather,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "player_form",
            "description": "Get a player's last N match stats this season — rating trend, goals, assists, shots.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player_name": {"type": "string"},
                    "last_n":      {"type": "integer", "default": 5}
                },
                "required": ["player_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "fatigue_check",
            "description": "Check if a player is fatigued based on minutes in last 3 matches. Returns HIGH or LOW risk.",
            "parameters": {
                "type": "object",
                "properties": {"player_name": {"type": "string"}},
                "required": ["player_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rank_position",
            "description": "Rank all players at a position by tactical fit score and current season form. Use G/D/M/F.",
            "parameters": {
                "type": "object",
                "properties": {"position": {"type": "string", "enum": ["G","D","M","F"]}},
                "required": ["position"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "squad_overview",
            "description": "Get the full squad with position, apps, rating and fatigue status for this season.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "compare_two",
            "description": "Side-by-side comparison of two players this season.",
            "parameters": {
                "type": "object",
                "properties": {
                    "player1": {"type": "string"},
                    "player2": {"type": "string"}
                },
                "required": ["player1","player2"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_injuries",
            "description": "Get current Brentford injury and suspension list.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_news",
            "description": "Search latest Brentford news and player updates.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "match_weather",
            "description": "Get match day weather forecast and its tactical impact.",
            "parameters": {
                "type": "object",
                "properties": {"match_date": {"type": "string", "description": "YYYY-MM-DD"}},
                "required": ["match_date"]
            }
        }
    }
]
