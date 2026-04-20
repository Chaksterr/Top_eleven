"""
Test script for NVIDIA NIM API integration
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "meta/llama-3.1-8b-instruct"

print("=" * 60)
print("NVIDIA NIM API Test")
print("=" * 60)
print(f"Model: {NVIDIA_MODEL}")
print(f"Base URL: {NVIDIA_BASE_URL}")
print(f"API Key: {'✓ Set' if NVIDIA_API_KEY else '✗ Not Set'}")
print("=" * 60)

if not NVIDIA_API_KEY:
    print("\n❌ ERROR: NVIDIA_API_KEY not found in .env file")
    print("\nTo get your API key:")
    print("1. Visit https://build.nvidia.com")
    print("2. Select any model (e.g., meta/llama-3.1-8b-instruct)")
    print("3. Click 'Get API Key'")
    print("4. Sign up for NVIDIA Developer Program (free)")
    print("5. Copy your API key")
    print("6. Add to .env: NVIDIA_API_KEY=your_key_here")
    exit(1)

print("\n🔵 Testing basic chat completion...")

try:
    llm = ChatOpenAI(
        model=NVIDIA_MODEL,
        api_key=NVIDIA_API_KEY,
        base_url=NVIDIA_BASE_URL,
        temperature=0.7,
        max_tokens=200
    )
    
    response = llm.invoke("Say 'Hello from NVIDIA NIM!' and nothing else.")
    print(f"✅ Response: {response.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)

print("\n🔵 Testing with a simple question...")

try:
    response = llm.invoke("What is 2+2? Answer in one sentence.")
    print(f"✅ Response: {response.content}")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    exit(1)

print("\n🔵 Testing with tool calling simulation...")

try:
    from langchain.tools import tool
    
    @tool
    def get_weather(location: str) -> str:
        """Get the weather for a location."""
        return f"The weather in {location} is sunny and 22°C"
    
    from langchain.agents import create_agent
    
    agent = create_agent(
        model=llm,
        tools=[get_weather],
        system_prompt="You are a helpful assistant. Use tools when needed."
    )
    
    result = agent.invoke({"messages": [("user", "What's the weather in London?")]})
    
    # Extract response
    messages = result.get("messages", [])
    if messages:
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                print(f"✅ Agent Response: {msg.content}")
                break
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! NVIDIA NIM is working correctly.")
print("=" * 60)
