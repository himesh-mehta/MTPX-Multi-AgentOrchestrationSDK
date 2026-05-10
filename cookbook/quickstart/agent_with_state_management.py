"""
🍳 MTP Cookbook — Agent with State Management
===========================================================
This example shows how to give your agent persistent state that it can
read and modify. The agent maintains a stock watchlist across conversations.

Different from storage (conversation history) and memory (user preferences),
state is structured data the agent actively manages: counters, lists, flags.

Key concepts:
- State Object: A Python dictionary holding structured data.
- Tools: Functions that modify the state.
- Dynamic Instructions: Injecting the state into the prompt before running.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_state_management.py
"""

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter
from mtp.session_store import JsonSessionStore

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------
# Global state for simplicity in this example
session_state = {
    "watchlist": []
}

# ---------------------------------------------------------------------------
# Custom Tools that Modify State
# ---------------------------------------------------------------------------
@mtp_tool(description="Add a stock ticker to the user's watchlist.")
def add_to_watchlist(ticker: str) -> str:
    """Add a stock ticker symbol (e.g., NVDA, AAPL) to the watchlist."""
    ticker = ticker.upper().strip()
    watchlist = session_state["watchlist"]

    if ticker in watchlist:
        return f"{ticker} is already on your watchlist."

    watchlist.append(ticker)
    return f"Added {ticker} to watchlist. Current watchlist: {', '.join(watchlist)}"


@mtp_tool(description="Remove a stock ticker from the user's watchlist.")
def remove_from_watchlist(ticker: str) -> str:
    """Remove a stock ticker symbol from the watchlist."""
    ticker = ticker.upper().strip()
    watchlist = session_state["watchlist"]

    if ticker not in watchlist:
        return f"{ticker} is not on your watchlist."

    watchlist.remove(ticker)
    if watchlist:
        return f"Removed {ticker}. Remaining watchlist: {', '.join(watchlist)}"
    return f"Removed {ticker}. Watchlist is now empty."


@mtp_tool(description="Get current market data for a stock.")
def get_market_data(ticker: str) -> str:
    db = {"NVDA": 187.90, "AAPL": 175.50, "GOOGL": 140.20, "AMD": 150.20}
    t = ticker.upper().strip()
    if t in db:
        return f"{t} is currently trading at ${db[t]}"
    return f"Data for {t} not available."


# ---------------------------------------------------------------------------
# Agent Configuration
# ---------------------------------------------------------------------------
def get_instructions() -> str:
    # Dynamically inject state into instructions
    watchlist = session_state["watchlist"]
    formatted_list = ", ".join(watchlist) if watchlist else "Empty"
    
    return f"""\
You are a Finance Agent that manages a stock watchlist.

## Current Watchlist State
Watchlist: [{formatted_list}]

## Capabilities
1. Manage watchlist
   - Add stocks: use add_to_watchlist tool
   - Remove stocks: use remove_from_watchlist tool

2. Get stock data
   - Use the get_market_data tool to fetch prices for watched stocks.

## Rules
- Always confirm watchlist changes.
- When asked about "my stocks" or "watchlist", refer to the Current Watchlist State above.
- Fetch fresh data when reporting on watchlist performance.\
"""

provider = OpenRouter(model="openai/gpt-oss-120b:free")

state_kit = Agent.toolkit_from_functions(
    "state_tools",
    add_to_watchlist,
    remove_from_watchlist,
    get_market_data
)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("core", state_kit)

# Initialize agent with session store so it remembers the conversation
agent_store = JsonSessionStore(db_path="tmp/state_sessions")
session_id = "watchlist-session"

agent_with_state = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=get_instructions(),
    session_store=agent_store,
)

# Wrapper to update instructions before each run
def run_agent(prompt: str) -> str:
    # Update instructions dynamically based on current state!
    agent_with_state._agent.instructions = get_instructions()
    return agent_with_state.run(prompt, session_id=session_id)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Agent with State Management")
    print("=" * 60)

    # 1. Add some stocks
    prompt1 = "Add NVDA, AAPL, and GOOGL to my watchlist"
    print(f"\n[User]: {prompt1}")
    print("-" * 30)
    response = run_agent(prompt1)
    print(f"Agent: {response}")

    # 2. Check the watchlist (Agent sees updated state in instructions!)
    prompt2 = "How are my watched stocks doing today?"
    print(f"\n[User]: {prompt2}")
    print("-" * 30)
    response = run_agent(prompt2)
    print(f"Agent: {response}")

    # View the state directly
    print("\n" + "=" * 60)
    print("Internal Python State:")
    print(f"  session_state['watchlist']: {session_state['watchlist']}")
    print("=" * 60)

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Agent with State Management
============================================================

[User]: Add NVDA, AAPL, and GOOGL to my watchlist
------------------------------
Agent: I have successfully added NVDA, AAPL, and GOOGL to your watchlist!

[User]: How are my watched stocks doing today?
------------------------------
Agent: Here is how the stocks on your current watchlist are performing today:
- **NVDA (NVIDIA):** Currently trading at $187.90
- **AAPL (Apple):** Currently trading at $175.50
- **GOOGL (Alphabet):** Currently trading at $140.20

Let me know if you want to add or remove any stocks!

============================================================
Internal Python State:
  session_state['watchlist']: ['NVDA', 'AAPL', 'GOOGL']
============================================================
"""
