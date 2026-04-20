"""
Test script for Assistant Coach Agent with NVIDIA NIM
"""

import sys
sys.path.insert(0, 'assistant_coach_langchain')

from agent import run_agent

print("=" * 60)
print("Assistant Coach Agent Test")
print("=" * 60)

# Test 1: Simple query
print("\n🔵 Test 1: Simple query")
print("Query: 'Who are the top 3 goalscorers this season?'")
print("-" * 60)

result = run_agent("Who are the top 3 goalscorers this season?")
print(f"\n✅ Response:\n{result['output']}")

# Test 2: Query with context
print("\n" + "=" * 60)
print("🔵 Test 2: Query with match context")
print("Query: 'Pick the best starting 11'")
print("Context: 'Opponent: Arsenal | Venue: Home'")
print("-" * 60)

result = run_agent(
    "Pick the best starting 11 for this match",
    match_context="Opponent: Arsenal | Venue: Home | Formation: 4-3-3"
)
print(f"\n✅ Response:\n{result['output'][:500]}...")

# Test 3: Player-specific query
print("\n" + "=" * 60)
print("🔵 Test 3: Player-specific query")
print("Query: 'How is Igor Thiago performing?'")
print("-" * 60)

result = run_agent("How is Igor Thiago performing this season?")
print(f"\n✅ Response:\n{result['output']}")

print("\n" + "=" * 60)
print("✅ All agent tests completed!")
print("=" * 60)
