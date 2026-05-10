"""
🍳 MTP Cookbook — Agent with Storage
====================================================
Building on the basic Agent, this example adds persistent storage.
Your agent now remembers conversations across runs.

Ask about NVDA, close the script, come back later — pick up where you left off.
The conversation history is saved to disk and restored automatically.

Key concepts:
- Run: Each time you run the agent via agent.run()
- Session: A conversation thread, identified by session_id
- Same session_id = continuous conversation, even across runs

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_storage.py
"""

import os
from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter
from mtp.session_store import JsonSessionStore

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Storage Configuration
# ---------------------------------------------------------------------------
os.makedirs("tmp", exist_ok=True)
agent_store = JsonSessionStore(db_path="tmp/sessions")

# ---------------------------------------------------------------------------
# Custom Finance Tool
# ---------------------------------------------------------------------------
@mtp_tool(description="Get current market data for a given ticker.")
def get_market_data(ticker: str) -> str:
    db = {
        "NVDA": {"price": 187.90, "market_cap": "4.6T", "pe": 45.5},
        "TSLA": {"price": 312.45, "market_cap": "995B", "pe": 65.2},
        "AAPL": {"price": 175.50, "market_cap": "2.7T", "pe": 28.4},
        "AMD":  {"price": 150.20, "market_cap": "242B", "pe": 40.1},
    }
    t = ticker.upper()
    return str(db.get(t, f"Data for {ticker} not found."))

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a Finance Agent — a data-driven analyst.
You must fetch market data using the tool and then provide concise insights.

## Rules
- Facts only, no speculation.
- Reference previous analyses in the conversation when relevant.
- Be extremely brief (2-3 sentences max).
"""

# ---------------------------------------------------------------------------
# Create the Agent
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

finance_kit = Agent.toolkit_from_functions("finance", get_market_data)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("finance", finance_kit)

agent_with_storage = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=instructions,
    session_store=agent_store,  # <--- This enables storage!
)

# ---------------------------------------------------------------------------
# Run the Agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Agent with Storage")
    print("=" * 60)

    # Use a consistent session_id to persist conversation across runs
    session_id = "finance-agent-session"

    print(f"\nUsing session_id: '{session_id}'\n")

    # Turn 1: Analyze a stock
    prompt1 = "Give me a quick investment brief on NVDA."
    print(f"[User]: {prompt1}")
    print("-" * 30)
    response = agent_with_storage.run(prompt1, session_id=session_id)
    print(f"Agent: {response}\n")

    # Turn 2: Compare — the agent remembers NVDA from turn 1
    prompt2 = "Compare that to Tesla (TSLA)."
    print(f"[User]: {prompt2}")
    print("-" * 30)
    response = agent_with_storage.run(prompt2, session_id=session_id)
    print(f"Agent: {response}\n")

    # Turn 3: Ask for a recommendation based on the full conversation
    prompt3 = "Based on our discussion, which looks like the better investment right now?"
    print(f"[User]: {prompt3}")
    print("-" * 30)
    response = agent_with_storage.run(prompt3, session_id=session_id)
    print(f"Agent: {response}\n")

    print("=" * 60)
    print("✅ Done! You can run this file again and the history will be intact.")
    print("=" * 60)

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Agent with Storage
============================================================

Using session_id: 'finance-agent-session'

[User]: Give me a quick investment brief on NVDA.
------------------------------
Agent: NVIDIA (NVDA) is currently priced at $187.90 with a massive market cap of 4.6T. It trades at a relatively high P/E ratio of 45.5, reflecting strong market expectations for its AI chip dominance.

[User]: Compare that to Tesla (TSLA).
------------------------------
Agent: Compared to NVIDIA, Tesla (TSLA) has a higher P/E ratio of 65.2 and a smaller market cap of 995B at a price of $312.45. While NVDA dominates AI hardware, Tesla's valuation leans heavily on future autonomous driving and energy expectations.

[User]: Based on our discussion, which looks like the better investment right now?
------------------------------
Agent: NVIDIA (NVDA) appears to be the more fundamentally sound investment right now. Despite a high P/E (45.5), its proven dominance in the booming AI sector and massive 4.6T market cap make it a safer growth play compared to Tesla's much higher P/E (65.2) and speculative valuation.

============================================================
✅ Done! You can run this file again and the history will be intact.
============================================================
"""
