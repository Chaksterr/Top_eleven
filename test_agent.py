import sys
sys.path.append('brentford_agent2')
from agent import run_agent
history = []
try:
    answer, history = run_agent("Who are the top performers this season?", history)
    print("SUCCESS")
    print(answer)
except Exception as e:
    import traceback
    traceback.print_exc()
