"""
agent.py
Agentic loop powered by Groq (llama-3.3-70b).
The LLM decides which tools to call, executes them, reasons over results,
and returns a final tactical recommendation to the coach.
"""

import os, json
from groq import Groq
from tools import TOOL_MAP, TOOL_SCHEMAS

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'item'):
            return obj.item()
        return super().default(obj)

SYSTEM = """
You are the elite AI Assistant Coach for Brentford FC (season 25/26), working directly under the Head Coach (the user).
Your role is to provide deep, data-driven tactical analysis, squad selection, and performance reviews.
Speak like a professional, top-tier Premier League coach. Use authentic terminology like 'Gaffer', 'transitions', 'pressing triggers', 'half-spaces', 'low block', and 'overloads'. Be analytical, concise, and highly confident in your data.

You ONLY analyse current season (25/26) data.
Default system: 4-3-3 high press, but you must adapt based on the opponent, venue, and weather conditions.

WHEN asked to pick a starting 11 or analyze the squad:
1. Call squad_overview first to get the baseline data.
2. Call get_injuries to immediately rule out unavailable players.
3. Call rank_position for specific roles (G, D, M, F).
4. Call fatigue_check for top candidates.
5. Call search_news for late fitness tests or club context.
6. Call match_weather if a date is provided, and adjust tactics accordingly (e.g., less passing from the back in heavy rain).
7. Synthesize everything into a cohesive, tactically sound lineup.

RULES:
- NEVER pick an injured or suspended player.
- Strongly advise resting players with HIGH fatigue (⚠️). Propose rotational options.
- Justify selections using hard data (form, ratings, specific stats) and tactical fit.
- Don't just list players; explain HOW they fit into the game plan against the specific opponent.

OUTPUT FORMAT for Starting 11:
## 📋 Match Day Squad — [Formation]
*Tactical Setup:* [Briefly explain why this formation/setup suits the opponent and conditions]

**GK:** [name] — [tactical/data reason]
**RB:** [name] — [tactical/data reason]
**CB:** [name] — [tactical/data reason]
**CB:** [name] — [tactical/data reason]
**LB:** [name] — [tactical/data reason]
**CDM:** [name] — [tactical/data reason]
**CM:** [name] — [tactical/data reason]
**CM:** [name] — [tactical/data reason]
**RW:** [name] — [tactical/data reason]
**LW:** [name] — [tactical/data reason]
**ST:** [name] — [tactical/data reason]

## 🔄 Impact Subs
- [name] — [reason for bringing them on later]
- [name] — [reason for bringing them on later]

## 🧠 Tactical Briefing
- **Key Battle:** [Where the game will be won or lost]
- **Pressing/Shape:** [How we approach without the ball]
"""

def run_agent(user_message: str, history: list = None) -> tuple[str, list]:
    """
    Agentic loop — runs until the LLM gives a final answer.
    Returns (answer, updated_history).
    """
    if history is None:
        history = []

    history.append({"role": "user", "content": user_message})
    messages = [{"role": "system", "content": SYSTEM}] + history

    MAX_STEPS = 10  # safety limit on tool calls

    for step in range(MAX_STEPS):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                max_tokens=4096,
                temperature=0.2
            )
        except groq.RateLimitError:
            try:
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=messages,
                    tools=TOOL_SCHEMAS,
                    tool_choice="auto",
                    max_tokens=4096,
                    temperature=0.2
                )
            except Exception as e:
                err_msg = f"⚠️ Rate limit hit. Please try again later.\n\nDetails: {str(e)}"
                history.append({"role": "assistant", "content": err_msg})
                return err_msg, history
        except Exception as e:
            err_msg = f"⚠️ API Error: {str(e)}"
            history.append({"role": "assistant", "content": err_msg})
            return err_msg, history

        msg   = response.choices[0].message
        calls = msg.tool_calls

        # No tool calls → final answer
        if not calls:
            answer = msg.content or "No answer generated."
            history.append({"role": "assistant", "content": answer})
            return answer, history

        # Execute tool calls
        messages.append({"role": "assistant", "content": msg.content or "", "tool_calls": [
            {"id": c.id, "type": "function",
             "function": {"name": c.function.name, "arguments": c.function.arguments}}
            for c in calls
        ]})

        for call in calls:
            fn_name = call.function.name
            try:
                fn_args = json.loads(call.function.arguments)
                if not isinstance(fn_args, dict):
                    fn_args = {}
            except Exception:
                fn_args = {}

            fn      = TOOL_MAP.get(fn_name)
            result  = fn(**fn_args) if fn else {"error": f"Unknown tool: {fn_name}"}

            messages.append({
                "role":         "tool",
                "tool_call_id": call.id,
                "content":      json.dumps(result, ensure_ascii=False, cls=NpEncoder)
            })

    # Fallback if max steps reached
    answer = "Analysis complete — maximum reasoning steps reached."
    history.append({"role": "assistant", "content": answer})
    return answer, history
