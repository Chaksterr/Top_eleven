"""
tools.py
LangChain tools for squad analysis and tactical decision-making
"""

import os
import pandas as pd
import requests
from langchain.tools import tool
from dotenv import load_dotenv
from config import CSV_PATH, CURRENT_SEASON, TACTICAL_PROFILE

load_dotenv()

# Load dataset
csv_paths = [
    CSV_PATH,
    "data/brentford_2021_2026.csv",  # Centralized data folder
    "brentford_2021_2026.csv",
    "assistant_coach/brentford_2021_2026.csv",
]

_raw = None
for path in csv_paths:
    if os.path.exists(path):
        print(f"✓ Loading CSV from: {path}")
        _raw = pd.read_csv(path)
        break

if _raw is None:
    raise FileNotFoundError(f"Could not find dataset. Tried: {csv_paths}")

df = _raw[_raw["season"] == CURRENT_SEASON].copy()


@tool
def squad_overview() -> dict:
    """Get full squad overview with position, apps, rating, and fatigue status for current season (25/26)."""
    result = []
    for player in df["player_name"].unique():
        player_data = df[df["player_name"] == player]
        
        # Calculate fatigue
        last_3 = player_data.sort_values("date").tail(3)
        minutes_last_3 = last_3["minutes_played"].sum()
        
        result.append({
            "player": player,
            "position": player_data["position"].iloc[0],
            "apps": len(player_data),
            "avg_rating": round(player_data["rating"].mean(), 2),
            "goals": int(player_data["goals"].sum()),
            "assists": int(player_data["assists"].sum()),
            "fatigued": minutes_last_3 >= TACTICAL_PROFILE["fatigue_threshold"]
        })
    
    return {"squad": sorted(result, key=lambda x: x["avg_rating"], reverse=True)}


@tool
def player_form(player_name: str, last_n: int = 5) -> dict:
    """Get a player's last N match stats including rating trend, goals, assists, and key metrics.
    
    Args:
        player_name: Name of the player
        last_n: Number of recent matches to analyze (default: 5)
    """
    player_data = df[df["player_name"].str.lower() == player_name.lower()]
    
    if player_data.empty:
        return {"error": f"'{player_name}' not found in season {CURRENT_SEASON}"}
    
    last_matches = player_data.sort_values("date").tail(last_n)
    
    return {
        "player": player_name,
        "matches_analyzed": len(last_matches),
        "avg_rating": round(last_matches["rating"].mean(), 2),
        "rating_trend": [round(r, 2) for r in last_matches["rating"].tolist()],
        "goals": int(last_matches["goals"].sum()),
        "assists": int(last_matches["assists"].sum()),
        "avg_shots": round(last_matches["shots"].mean(), 2),
        "avg_minutes": round(last_matches["minutes_played"].mean(), 1),
        "avg_key_passes": round(last_matches["key_passes"].mean(), 2),
        "avg_tackles_won": round(last_matches["tackles_won"].mean(), 2),
        "position": player_data["position"].iloc[0]
    }


@tool
def fatigue_check(player_name: str) -> dict:
    """Check if a player is fatigued based on minutes played in last 3 matches.
    
    Args:
        player_name: Name of the player to check
    """
    player_data = df[df["player_name"].str.lower() == player_name.lower()]
    
    if player_data.empty:
        return {"error": f"'{player_name}' not found"}
    
    last_3 = player_data.sort_values("date").tail(3)
    total_minutes = round(last_3["minutes_played"].sum(), 0)
    threshold = TACTICAL_PROFILE["fatigue_threshold"]
    
    return {
        "player": player_name,
        "minutes_last_3": total_minutes,
        "threshold": threshold,
        "fatigued": total_minutes >= threshold,
        "risk": "HIGH ⚠️" if total_minutes >= threshold else "LOW ✅"
    }


@tool
def rank_position(position: str) -> dict:
    """Rank all players at a position by tactical fit and current season form.
    
    Args:
        position: Position code (G=Goalkeeper, D=Defender, M=Midfielder, F=Forward)
    """
    pos_df = df[df["position"] == position.upper()]
    
    if pos_df.empty:
        return {"error": f"No players for position '{position}'"}
    
    # Get position-specific metrics
    metrics = TACTICAL_PROFILE["position_priorities"].get(position.upper(), ["rating"])
    metrics = [m for m in metrics if m in pos_df.columns]
    
    if not metrics:
        metrics = ["rating"]
    
    # Aggregate by player
    agg = pos_df.groupby("player_name")[metrics + ["minutes_played"]].mean().reset_index()
    
    # Normalize metrics
    for metric in metrics:
        min_val, max_val = agg[metric].min(), agg[metric].max()
        agg[f"{metric}_norm"] = (agg[metric] - min_val) / (max_val - min_val + 1e-9)
    
    # Calculate composite score
    agg["score"] = agg[[f"{m}_norm" for m in metrics]].mean(axis=1).round(3)
    
    # Rank players
    ranked = agg.sort_values("score", ascending=False)[["player_name", "score"] + metrics].head(6)
    
    return {
        "position": position.upper(),
        "players": ranked.to_dict(orient="records")
    }


@tool
def compare_two(player1: str, player2: str) -> dict:
    """Side-by-side comparison of two players this season.
    
    Args:
        player1: First player name
        player2: Second player name
    """
    def get_stats(name):
        player_data = df[df["player_name"].str.lower() == name.lower()]
        if player_data.empty:
            return {"error": f"'{name}' not found"}
        
        return {
            "player": name,
            "position": player_data["position"].iloc[0],
            "apps": len(player_data),
            "avg_rating": round(player_data["rating"].mean(), 2),
            "goals": int(player_data["goals"].sum()),
            "assists": int(player_data["assists"].sum()),
            "avg_shots": round(player_data["shots"].mean(), 2),
            "avg_key_passes": round(player_data["key_passes"].mean(), 2),
            "avg_tackles_won": round(player_data["tackles_won"].mean(), 2),
            "avg_minutes": round(player_data["minutes_played"].mean(), 1)
        }
    
    return {
        "player1": get_stats(player1),
        "player2": get_stats(player2)
    }


@tool
def get_injuries() -> dict:
    """Fetch current Brentford injury and suspension list from API-Football."""
    key = os.getenv("APIFOOTBALL_KEY", "") or os.getenv("FOOTBALLDATA_KEY", "")
    
    if not key:
        return {
            "injuries": [],
            "note": "Add APIFOOTBALL_KEY to .env for live injury data"
        }
    
    try:
        response = requests.get(
            "https://v3.football.api-sports.io/injuries",
            headers={"x-apisports-key": key},
            params={"team": 55, "season": 2025},
            timeout=8
        )
        data = response.json().get("response", [])
        
        return {
            "injuries": [
                {
                    "player": injury["player"]["name"],
                    "reason": injury["player"].get("reason", "unknown")
                }
                for injury in data
            ]
        }
    except Exception as e:
        return {"injuries": [], "error": str(e)}


@tool
def search_news(query: str) -> dict:
    """Search latest Brentford news via Tavily.
    
    Args:
        query: Search query (e.g., "player fitness", "tactical changes")
    """
    key = os.getenv("TAVILY_KEY", "")
    
    if not key:
        return {
            "results": [],
            "note": "Add TAVILY_KEY to .env for live news"
        }
    
    try:
        from tavily import TavilyClient
        client = TavilyClient(api_key=key)
        results = client.search(f"Brentford FC {query} 2025", max_results=3)
        
        return {
            "results": [
                {
                    "title": r["title"],
                    "summary": r["content"][:250]
                }
                for r in results.get("results", [])
            ]
        }
    except Exception as e:
        return {"results": [], "error": str(e)}


@tool
def match_weather(match_date: str) -> dict:
    """Get match day weather forecast at Brentford Community Stadium (free, no key needed).
    
    Args:
        match_date: Match date in YYYY-MM-DD format
    """
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 51.4882,
                "longitude": -0.3088,
                "daily": "precipitation_sum,windspeed_10m_max,temperature_2m_max",
                "timezone": "Europe/London",
                "start_date": match_date,
                "end_date": match_date
            },
            timeout=8
        )
        data = response.json()
        daily = data.get("daily", {})
        
        rain = (daily.get("precipitation_sum") or [0])[0] or 0
        wind = (daily.get("windspeed_10m_max") or [0])[0] or 0
        temp = (daily.get("temperature_2m_max") or [0])[0] or 0
        
        impact = "rainy — expect less possession play" if rain > 2 else \
                 "windy — long balls less effective" if wind > 30 else \
                 "good conditions"
        
        return {
            "date": match_date,
            "temperature_c": temp,
            "wind_kmh": wind,
            "rain_mm": rain,
            "impact": impact
        }
    except Exception as e:
        return {"error": str(e)}


# Export all tools as a list
TOOLS = [
    squad_overview,
    player_form,
    fatigue_check,
    rank_position,
    compare_two,
    get_injuries,
    search_news,
    match_weather
]
