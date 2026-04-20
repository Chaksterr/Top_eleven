"""
agent.py
LangChain agent setup with NVIDIA NIM (using LangChain v1.0 API)
"""

import uuid
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from tools import TOOLS
from config import NVIDIA_API_KEY, NVIDIA_BASE_URL, NVIDIA_MODEL, SYSTEM_PROMPT


def get_llm():
    """Create a fresh LLM instance using NVIDIA NIM."""
    return ChatOpenAI(
        model=NVIDIA_MODEL,
        api_key=NVIDIA_API_KEY,
        base_url=NVIDIA_BASE_URL,
        temperature=0.7,
        max_tokens=4096
    )


def run_agent(user_message: str, match_context: str = "") -> dict:
    """
    Run the LangChain agent with user message and optional match context.
    
    Args:
        user_message: User's question or request
        match_context: Optional match context (opponent, venue, etc.)
    
    Returns:
        dict with 'output' and 'messages'
    """
    # Build the full message with context
    full_message = user_message
    if match_context:
        full_message = f"[Match Context: {match_context}]\n\n{user_message}"
    
    print(f"\n🔵 Processing query: {user_message[:50]}...")
    
    try:
        # Create a fresh agent for each request to avoid state issues
        llm = get_llm()
        agent = create_agent(
            model=llm,
            tools=TOOLS,
            system_prompt=SYSTEM_PROMPT
        )
        
        # Create a fresh message list for each invocation
        messages = [("user", full_message)]
        
        print(f"🔵 Invoking agent with {len(TOOLS)} tools available...")
        
        # Invoke the agent
        result = agent.invoke({"messages": messages})
        
        print(f"🟢 Agent completed")
        
        # Extract the final response from messages
        result_messages = result.get("messages", [])
        output = ""
        if result_messages:
            # Get the last AI message
            for msg in reversed(result_messages):
                if hasattr(msg, 'content') and msg.content:
                    output = msg.content
                    break
        
        return {
            "output": output or "No response generated.",
            "messages": result_messages
        }
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"🔴 Error: {str(e)}")
        return {
            "output": f"⚠️ Error: {str(e)}\n\nPlease try rephrasing your question or check your API key.",
            "messages": []
        }
