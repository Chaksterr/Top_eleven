"""
app.py — Streamlit chat interface for the Brentford Assistant Coach
"""

import streamlit as st
from dotenv import load_dotenv
import os, json, datetime
load_dotenv()

from agent import run_agent, client as groq_client

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Brentford Assistant Coach",
    page_icon="🐝",
    layout="wide"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

/* Base Font & Dynamic Background */
html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
.stApp { 
    background: radial-gradient(circle at top left, #16162A, #0A0A12);
    color: #E2E8F0;
}

/* Glassmorphic Sidebar */
section[data-testid="stSidebar"] { 
    background: rgba(20, 20, 35, 0.4) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

/* Premium Buttons with Micro-animations */
.stButton > button {
    background: linear-gradient(135deg, #D0021B, #9A0010);
    color: white; 
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; 
    font-weight: 700; 
    width: 100%;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    box-shadow: 0 4px 15px rgba(208, 2, 27, 0.2);
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(208, 2, 27, 0.4);
    border: 1px solid rgba(255,255,255,0.3);
}

/* Chat Message Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(30, 30, 45, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1rem;
    backdrop-filter: blur(8px);
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=86400)
def fetch_brentford_fixtures():
    key = os.getenv("TAVILY_KEY", "")
    if not key:
        return []
    try:
        from tavily import TavilyClient
        tc = TavilyClient(api_key=key)
        res = tc.search("Brentford FC full complete fixture list remaining premier league season 2025 2026 dates opponents", max_results=10)
        context = "\n".join([r['content'] for r in res.get('results', [])])
        
        prompt = f"""Extract ALL of Brentford FC's upcoming matches from this text in chronological order.
Return ONLY a JSON object with a key "fixtures" containing an array of ALL matches found. 
Each object must have "opponent" (string) and "date" (YYYY-MM-DD string). Don't miss any fixtures.
Text: {context}"""
        
        try:
            comp = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
        except Exception: # Catch rate limit or others
            comp = groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0
            )
        data = json.loads(comp.choices[0].message.content)
        return data.get("fixtures", [])
    except Exception as e:
        print(f"Fixture fetch error: {e}")
        return []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🐝 BRENTFORD FC")
    st.markdown("**Assistant Coach · Season 25/26**")
    st.divider()

    st.markdown("#### Match Context")
    
    # Live Fixtures Logic
    fixtures = fetch_brentford_fixtures()
    opponent_opts = ["Manual Entry"] + [f["opponent"] for f in fixtures]
    selected_opp_label = st.selectbox("Opponent", opponent_opts)
    
    if selected_opp_label == "Manual Entry":
        opponent = st.text_input("Manual Opponent", placeholder="e.g. Arsenal")
        match_date = st.date_input("Match Date")
    else:
        opponent = selected_opp_label
        # Find the date
        default_date = datetime.date.today()
        for f in fixtures:
            if f["opponent"] == selected_opp_label:
                try:
                    default_date = datetime.datetime.strptime(f["date"], "%Y-%m-%d").date()
                except:
                    pass
                break
        match_date = st.date_input("Match Date", value=default_date)

    venue       = st.selectbox("Venue",        ["Home", "Away", "Neutral"])
    competition = st.selectbox("Competition",  ["Premier League", "FA Cup", "EFL Cup"])
    formation   = st.selectbox("Formation",    ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"])
    style       = st.selectbox("Our Style",    ["High Press", "Possession", "Counter-Attack"])

    st.divider()
    st.markdown("#### Quick Actions")
    b1 = st.button("🔴 Pick best starting 11")
    b2 = st.button("⚡ Who needs rest?")
    b3 = st.button("📈 Top performers this season")
    b4 = st.button("🔄 Best bench options")
    b5 = st.button("🌦️ Match day weather impact")

    st.divider()
    st.caption("Powered by Groq · llama-3.3-70b")
    st.caption("Data: Brentford FC 25/26 season")

# ── Session state ─────────────────────────────────────────────────────────────
if "history"  not in st.session_state: st.session_state.history  = []
if "messages" not in st.session_state: st.session_state.messages = []

# ── Header ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("# 🐝 Brentford Assistant Coach")
    st.markdown("Ask about players, form, tactics or request a starting 11 for the next match.")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Chat"):
        st.session_state.history  = []
        st.session_state.messages = []
        st.rerun()

st.divider()

# ── Context builder ───────────────────────────────────────────────────────────
def context():
    parts = []
    if opponent:    parts.append(f"Opponent: {opponent}")
    if venue:       parts.append(f"Venue: {venue}")
    if competition: parts.append(f"Competition: {competition}")
    if match_date:  parts.append(f"Date: {match_date}")
    if formation:   parts.append(f"Formation: {formation}")
    if style:       parts.append(f"Style: {style}")
    return " | ".join(parts)

# ── Quick action triggers ─────────────────────────────────────────────────────
ctx   = context()
quick = None
if b1: quick = f"Pick the best starting 11 for our next match. {ctx}"
if b2: quick = "Which players need rest this week based on their minutes in the last 3 matches?"
if b3: quick = "Who are the top performers this season? Rank by position."
if b4: quick = "Who are the best substitution options from the bench right now?"
if b5: quick = f"What is the weather forecast for match day {match_date} and how does it affect our tactics?"

# ── Display history ───────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🐝"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ── Input ─────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask anything about the squad, form or tactics...") or quick

if user_input:
    full = f"{user_input}\n[Current Match Context: {ctx}]" if ctx else user_input
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Immediate user message draw
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🐝"):
        with st.spinner("🐝 Analysing squad data..."):
            answer, st.session_state.history = run_agent(full, st.session_state.history)
        st.markdown(answer)
        
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
