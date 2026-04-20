"""
config.py
Configuration and system prompts for the LangChain Assistant Coach
"""

import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration - Using NVIDIA NIM (Free Tier with OpenAI-compatible API)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "meta/llama-3.1-8b-instruct"  # Lighter, faster model (8B parameters)

# CSV Configuration
CSV_PATH = os.getenv("ASSISTANT_COACH_CSV_PATH", "data/brentford_2021_2026.csv")
CURRENT_SEASON = "25/26"

# Tactical Configuration
TACTICAL_PROFILE = {
    "formation": "4-3-3",
    "style": "high_press",
    "fatigue_threshold": 240,  # minutes in last 3 games
    "position_priorities": {
        "F": ["goals", "shots", "assists", "rating"],
        "M": ["tackles_won", "key_passes", "accurate_passes", "rating"],
        "D": ["clearances", "interceptions", "aerial_duels_won", "rating"],
        "G": ["rating", "saves"]
    }
}

# System Prompt (simplified for better compatibility)
SYSTEM_PROMPT = """You are an AI Assistant Coach for Brentford FC (season 25/26).

Your role: Provide data-driven tactical analysis, squad selection, and performance reviews.

Key rules:
- ALWAYS use tools to get current data before answering
- NEVER pick injured or suspended players
- Justify selections with data (ratings, form, stats)
- Default formation: 4-3-3 high press

When picking a starting 11:
1. Call squad_overview for baseline data
2. Call get_injuries to check availability
3. Call rank_position for each position (G, D, M, F)
4. Call fatigue_check for top candidates
5. Provide tactical reasoning for each selection"""

# Streamlit Configuration
STREAMLIT_CONFIG = {
    "page_title": "Brentford Assistant Coach (LangChain)",
    "page_icon": "🐝",
    "layout": "wide"
}
