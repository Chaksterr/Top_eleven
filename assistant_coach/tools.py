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


@tool
def analyze_opponent(opponent_name: str) -> dict:
    """Analyze opponent team's tactics, strengths, weaknesses, and provide strategic recommendations.
    Fetches real data from API-Football for team statistics and recent form.
    Use this tool when asked about how to play against a specific team or what tactics to use.
    
    Args:
        opponent_name: Name of the opponent team (e.g., "Arsenal", "Chelsea", "Liverpool")
    """
    api_key = os.getenv("APIFOOTBALL_KEY", "") or os.getenv("FOOTBALLDATA_KEY", "")
    
    if not api_key:
        return {
            "team": opponent_name,
            "error": "API-Football key not configured",
            "note": "Add APIFOOTBALL_KEY to .env for live opponent analysis",
            "fallback_advice": [
                "Focus on our tactical strengths",
                "Maintain defensive discipline",
                "Exploit counter-attacking opportunities"
            ]
        }
    
    try:
        # Premier League team ID mapping (common teams)
        team_ids = {
            "arsenal": 42, "chelsea": 49, "liverpool": 40, "manchester city": 50,
            "manchester united": 33, "tottenham": 47, "newcastle": 34, "aston villa": 66,
            "brighton": 51, "west ham": 48, "crystal palace": 52, "fulham": 36,
            "wolves": 39, "everton": 45, "nottingham forest": 65, "bournemouth": 35,
            "luton": 163, "burnley": 44, "sheffield united": 62, "brentford": 55
        }
        
        opponent_key = opponent_name.lower().strip()
        team_id = team_ids.get(opponent_key)
        
        if not team_id:
            # Try to search for team
            search_response = requests.get(
                "https://v3.football.api-sports.io/teams",
                headers={"x-apisports-key": api_key},
                params={"search": opponent_name, "league": 39, "season": 2025},
                timeout=10
            )
            search_data = search_response.json().get("response", [])
            if search_data:
                team_id = search_data[0]["team"]["id"]
            else:
                return {
                    "team": opponent_name,
                    "error": f"Team '{opponent_name}' not found in Premier League",
                    "note": "Please check the team name spelling"
                }
        
        # Fetch team statistics for current season
        stats_response = requests.get(
            "https://v3.football.api-sports.io/teams/statistics",
            headers={"x-apisports-key": api_key},
            params={"team": team_id, "season": 2025, "league": 39},
            timeout=10
        )
        stats_data = stats_response.json().get("response", {})
        
        # Fetch last 5 fixtures
        fixtures_response = requests.get(
            "https://v3.football.api-sports.io/fixtures",
            headers={"x-apisports-key": api_key},
            params={"team": team_id, "last": 5, "season": 2025, "league": 39},
            timeout=10
        )
        fixtures_data = fixtures_response.json().get("response", [])
        
        # Parse statistics
        form = stats_data.get("form", "N/A")
        fixtures_played = stats_data.get("fixtures", {})
        goals_stats = stats_data.get("goals", {}).get("for", {})
        goals_against = stats_data.get("goals", {}).get("against", {})
        
        # Calculate recent form from fixtures
        recent_results = []
        for fixture in fixtures_data[:5]:
            home_team = fixture["teams"]["home"]["id"]
            home_goals = fixture["goals"]["home"]
            away_goals = fixture["goals"]["away"]
            
            if home_team == team_id:
                if home_goals > away_goals:
                    recent_results.append("W")
                elif home_goals < away_goals:
                    recent_results.append("L")
                else:
                    recent_results.append("D")
            else:
                if away_goals > home_goals:
                    recent_results.append("W")
                elif away_goals < home_goals:
                    recent_results.append("L")
                else:
                    recent_results.append("D")
        
        recent_form = "-".join(recent_results) if recent_results else form
        
        # Build analysis
        avg_goals_for = goals_stats.get("average", {}).get("total", 0)
        avg_goals_against = goals_against.get("average", {}).get("total", 0)
        
        # Determine strengths and weaknesses based on stats
        strengths = []
        weaknesses = []
        
        if avg_goals_for and float(avg_goals_for) > 1.5:
            strengths.append(f"Strong attacking output ({avg_goals_for} goals/game average)")
        else:
            weaknesses.append(f"Limited goal threat ({avg_goals_for} goals/game average)")
        
        if avg_goals_against and float(avg_goals_against) < 1.0:
            strengths.append(f"Solid defensive record ({avg_goals_against} conceded/game)")
        else:
            weaknesses.append(f"Defensive vulnerabilities ({avg_goals_against} conceded/game)")
        
        wins = fixtures_played.get("wins", {}).get("total", 0)
        played = fixtures_played.get("played", {}).get("total", 1)
        win_rate = (wins / played * 100) if played > 0 else 0
        
        if win_rate > 50:
            strengths.append(f"Strong win rate ({win_rate:.0f}%)")
        
        # Tactical recommendations based on data
        recommendations = []
        
        if avg_goals_against and float(avg_goals_against) > 1.2:
            recommendations.append("Exploit defensive weaknesses with quick attacks")
            recommendations.append("Target set-pieces and crosses into the box")
        
        if avg_goals_for and float(avg_goals_for) > 1.8:
            recommendations.append("Deploy compact defensive shape to limit space")
            recommendations.append("Focus on defensive discipline and organization")
        
        recommendations.extend([
            "Press high when they build from the back",
            "Quick transitions to exploit counter-attacking opportunities",
            "Double-mark their key creative players"
        ])
        
        return {
            "team": opponent_name.title(),
            "recent_form": recent_form,
            "matches_played": played,
            "wins": wins,
            "win_rate_percent": round(win_rate, 1),
            "avg_goals_scored": avg_goals_for,
            "avg_goals_conceded": avg_goals_against,
            "strengths": strengths if strengths else ["Balanced team profile"],
            "weaknesses": weaknesses if weaknesses else ["No clear weaknesses identified"],
            "tactical_recommendations": recommendations,
            "data_source": "API-Football (live data)"
        }
        
    except requests.exceptions.Timeout:
        return {
            "team": opponent_name,
            "error": "API request timed out",
            "note": "Try again or check your internet connection"
        }
    except Exception as e:
        return {
            "team": opponent_name,
            "error": f"Failed to fetch opponent data: {str(e)}",
            "note": "Check API key and internet connection"
        }


# Export all tools as a list
TOOLS = [
    squad_overview,
    player_form,
    fatigue_check,
    rank_position,
    compare_two,
    get_injuries,
    search_news,
    match_weather,
    analyze_opponent
]
