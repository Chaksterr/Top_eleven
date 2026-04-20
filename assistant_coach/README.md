# 🐝 Brentford FC Assistant Coach - LangChain Version

AI-powered tactical assistant using **LangChain** framework with **xAI Grok** LLM.

## Features

- 🤖 LangChain agent with tool orchestration
- 💬 Conversation memory for context-aware responses
- 🔧 Modular tool system for squad analysis
- 📊 Real-time data integration (injuries, weather, news)
- ⚡ Streamlit chat interface

## Architecture

```
assistant_coach_langchain/
├── app.py              # Streamlit frontend
├── agent.py            # LangChain agent setup
├── tools.py            # LangChain tools (squad analysis)
├── memory.py           # Conversation memory management
├── config.py           # Configuration and prompts
└── requirements.txt    # Dependencies
```

## Setup

```bash
# Copy the root .env.example to .env
cp .env.example .env

# Edit .env and add your xAI API key
# XAI_API_KEY=xai-your_actual_key_here

# Sync dependencies (LangChain packages already in pyproject.toml)
uv sync

# Run
uv run streamlit run assistant_coach_langchain/app.py
```

## Usage

Ask tactical questions:
- "Pick the best starting 11 vs Arsenal"
- "Who needs rest this week?"
- "Compare Toney and Mbeumo"
- "Analyze our defensive weaknesses"

## LangChain Components

- **Agent**: ReAct agent with tool calling
- **LLM**: xAI Grok via OpenAI-compatible API
- **Tools**: Custom LangChain tools for squad analysis
- **Memory**: ConversationBufferMemory for chat history
- **Callbacks**: Streamlit callback handler for real-time updates
