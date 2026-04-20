"""
app.py
Streamlit chat interface for LangChain-based Brentford Assistant Coach
"""

import streamlit as st
import datetime
from config import STREAMLIT_CONFIG
from agent import run_agent

# Page config
st.set_page_config(**STREAMLIT_CONFIG)

# CSS Styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"] { 
    font-family: 'Outfit', sans-serif; 
}

.stApp { 
    background: radial-gradient(circle at top left, #16162A, #0A0A12);
    color: #FFFFFF;
}

section[data-testid="stSidebar"] { 
    background: rgba(20, 20, 35, 0.4) !important;
    backdrop-filter: blur(12px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

.stButton > button {
    background: linear-gradient(135deg, #D0021B, #9A0010);
    color: white; 
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; 
    font-weight: 700; 
    width: 100%;
    transition: all 0.3s;
    box-shadow: 0 4px 15px rgba(208, 2, 27, 0.2);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(208, 2, 27, 0.4);
}

/* Chat message styling */
[data-testid="stChatMessage"] {
    background: rgba(30, 30, 45, 0.6) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
    margin-bottom: 1rem !important;
    backdrop-filter: blur(8px) !important;
}

/* Make all chat text white */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] span,
[data-testid="stChatMessage"] div,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] h1,
[data-testid="stChatMessage"] h2,
[data-testid="stChatMessage"] h3,
[data-testid="stChatMessage"] h4,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em {
    color: #FFFFFF !important;
}

/* Chat input styling */
[data-testid="stChatInput"] {
    background: rgba(30, 30, 45, 0.8) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] input {
    color: #FFFFFF !important;
}

/* Markdown content in chat */
.stMarkdown {
    color: #FFFFFF !important;
}

/* Code blocks in chat */
code {
    background: rgba(0, 0, 0, 0.3) !important;
    color: #FFFFFF !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
}

/* Expander styling */
[data-testid="stExpander"] {
    background: rgba(20, 20, 35, 0.5) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 8px !important;
}

[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div {
    color: #FFFFFF !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label {
    color: #E2E8F0 !important;
}

/* Main content text */
.main p, .main span, .main div {
    color: #FFFFFF !important;
}

/* Headers */
h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## 🐝 BRENTFORD FC")
    st.markdown("**Assistant Coach · LangChain Edition**")
    st.markdown("*Season 25/26*")
    st.divider()

    st.markdown("#### Match Context")
    
    opponent = st.text_input("Opponent", placeholder="e.g. Arsenal")
    match_date = st.date_input("Match Date", value=datetime.date.today())
    venue = st.selectbox("Venue", ["Home", "Away", "Neutral"])
    competition = st.selectbox("Competition", ["Premier League", "FA Cup", "EFL Cup"])
    formation = st.selectbox("Formation", ["4-3-3", "4-2-3-1", "3-5-2", "4-4-2"])
    style = st.selectbox("Our Style", ["High Press", "Possession", "Counter-Attack"])

    st.divider()
    st.markdown("#### Quick Actions")
    b1 = st.button("🔴 Pick best starting 11")
    b2 = st.button("⚡ Who needs rest?")
    b3 = st.button("📈 Top performers this season")
    b4 = st.button("🔄 Best bench options")
    b5 = st.button("🌦️ Match day weather impact")

    st.divider()
    st.caption("🔗 Powered by LangChain + NVIDIA NIM")
    st.caption("📊 Data: Brentford FC 25/26 season")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Header
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown("# 🐝 Brentford Assistant Coach")
    st.markdown("*LangChain Edition with NVIDIA NIM*")
    st.markdown("Ask about players, form, tactics or request a starting 11 for the next match.")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.divider()

# Build context string
def build_context():
    parts = []
    if opponent:
        parts.append(f"Opponent: {opponent}")
    if venue:
        parts.append(f"Venue: {venue}")
    if competition:
        parts.append(f"Competition: {competition}")
    if match_date:
        parts.append(f"Date: {match_date}")
    if formation:
        parts.append(f"Formation: {formation}")
    if style:
        parts.append(f"Style: {style}")
    return " | ".join(parts)

# Quick action triggers
ctx = build_context()
quick = None
if b1:
    quick = f"Pick the best starting 11 for our next match. {ctx}"
if b2:
    quick = "Which players need rest this week based on their minutes in the last 3 matches?"
if b3:
    quick = "Who are the top performers this season? Rank by position."
if b4:
    quick = "Who are the best substitution options from the bench right now?"
if b5:
    quick = f"What is the weather forecast for match day {match_date} and how does it affect our tactics?"

# Display chat history
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🐝"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Ask anything about the squad, form or tactics...") or quick

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    # Get agent response
    with st.chat_message("assistant", avatar="🐝"):
        with st.spinner("🐝 Analyzing squad data with LangChain..."):
            result = run_agent(user_input, ctx)
            answer = result["output"]
        
        st.markdown(answer)
        
        # Show intermediate steps in expander (optional)
        if result.get("intermediate_steps"):
            with st.expander("🔍 View Agent Reasoning Steps"):
                for i, (action, observation) in enumerate(result["intermediate_steps"], 1):
                    st.markdown(f"**Step {i}:**")
                    st.code(f"Tool: {action.tool}\nInput: {action.tool_input}", language="text")
                    st.text(f"Result: {observation[:200]}...")
                    st.divider()
    
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.rerun()
