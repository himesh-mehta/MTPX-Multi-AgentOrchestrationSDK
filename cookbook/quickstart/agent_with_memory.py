"""
🍳 MTP Cookbook — Agent with Memory
=====================================================
This example shows how to give your agent memory of user preferences.
The agent remembers facts about you across all conversations.

Different from session storage (which persists conversation history), memory
persists user-level information: preferences, facts, context.

Key concepts:
- Agentic Memory: The agent decides when to store/recall via tool calls
- Memory Storage: A JSON file or database storing user_id -> facts

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_memory.py
"""

import json
import os
from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Simple Memory Manager Implementation
# ---------------------------------------------------------------------------
class SimpleMemoryManager:
    """A lightweight memory manager that persists user facts to disk."""
    
    def __init__(self, memory_file: str = "tmp/user_memory.json"):
        self.memory_file = memory_file
        self.memories = self._load()

    def _load(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save(self):
        os.makedirs(os.path.dirname(self.memory_file) or ".", exist_ok=True)
        with open(self.memory_file, "w") as f:
            json.dump(self.memories, f, indent=2)

    def add_memory(self, user_id: str, fact: str):
        if user_id not in self.memories:
            self.memories[user_id] = []
        self.memories[user_id].append(fact)
        self._save()

    def get_memories(self, user_id: str) -> list:
        return self.memories.get(user_id, [])

# Initialize memory manager
memory_manager = SimpleMemoryManager()
# Global state for current user to avoid passing it to tool explicitly in basic setups
CURRENT_USER_ID = "investor@example.com"

# ---------------------------------------------------------------------------
# Agentic Memory Tools
# ---------------------------------------------------------------------------
@mtp_tool(description="Save a new preference or fact about the current user.")
def save_user_preference(fact: str) -> str:
    """Use this tool when the user shares their investment goals, risk tolerance, or favorite sectors."""
    memory_manager.add_memory(CURRENT_USER_ID, fact)
    return f"Successfully saved memory: {fact}"

@mtp_tool(description="Retrieve all saved preferences and facts about the current user.")
def get_user_preferences() -> str:
    """Use this tool to load the user's saved investment profile before making recommendations."""
    memories = memory_manager.get_memories(CURRENT_USER_ID)
    if not memories:
        return "No memories saved for this user."
    return "User Preferences:\n- " + "\n- ".join(memories)

# ---------------------------------------------------------------------------
# Finance Tool
# ---------------------------------------------------------------------------
@mtp_tool(description="Get market data for a given ticker symbol.")
def get_market_data(ticker: str) -> str:
    db = {"NVDA": {"price": 187.90}, "AAPL": {"price": 175.50}, "TSLA": {"price": 312.45}}
    t = ticker.upper()
    if t in db:
        return f"{t} current price is ${db[t]['price']}"
    return f"Data not found for {ticker}"

# ---------------------------------------------------------------------------
# Create the Agent
# ---------------------------------------------------------------------------
instructions = """\
You are a Finance Agent.
You have access to memory tools to save and recall user preferences.

## Memory Rules:
1. If the user tells you about their preferences (e.g. risk tolerance, favorite sectors),
   immediately call `save_user_preference` to store it.
2. Before answering recommendation requests, ALWAYS call `get_user_preferences` to
   tailor your response to the user's stored profile.

## Workflow:
- Fetch market data when analyzing stocks.
- Tailor recommendations using the user's memory profile.
"""

provider = OpenRouter(model="openai/gpt-oss-120b:free")

# Register tools
memory_kit = Agent.toolkit_from_functions(
    "memory_and_finance", 
    save_user_preference, 
    get_user_preferences,
    get_market_data
)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("core", memory_kit)

agent_with_memory = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=instructions,
)

# ---------------------------------------------------------------------------
# Run the Agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print(f"  MTP Cookbook — Agent with Memory (User: {CURRENT_USER_ID})")
    print("=" * 60)

    # 1. Share preferences
    prompt1 = "I'm interested in AI and semiconductor stocks. My risk tolerance is moderate."
    print(f"\n[User]: {prompt1}")
    print("-" * 30)
    response = agent_with_memory.run(prompt1)
    print(f"Agent: {response}")

    # 2. Ask for a recommendation based on those preferences
    # Notice we ask broadly, and the agent uses memory to narrow it down!
    prompt2 = "What stocks would you recommend for me?"
    print(f"\n[User]: {prompt2}")
    print("-" * 30)
    response = agent_with_memory.run(prompt2)
    print(f"Agent: {response}")

    # View stored memories directly
    memories = memory_manager.get_memories(CURRENT_USER_ID)
    print("\n" + "=" * 60)
    print("Stored Memories in tmp/user_memory.json:")
    print("=" * 60)
    for m in memories:
        print(f"  • {m}")
    
    print("\n✅ Done! The agent learned your preferences and used them.")

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Agent with Memory (User: investor@example.com)
============================================================

[User]: I'm interested in AI and semiconductor stocks. My risk tolerance is moderate.
------------------------------
Agent: I've noted that you are interested in AI and semiconductor stocks, and that your risk tolerance is moderate. 
Let me know when you'd like to explore some investment options!

[User]: What stocks would you recommend for me?
------------------------------
Agent: Based on your preference for AI and semiconductor stocks with a moderate risk tolerance, here are two recommendations:

1. **NVIDIA (NVDA):** Currently priced at $187.90. It's the market leader in AI hardware and offers solid growth, fitting a moderate risk profile perfectly compared to highly speculative smaller players.
2. **Apple (AAPL):** At $175.50, it provides a stable foundation with increasing exposure to AI via its custom silicon (Apple Silicon) and consumer AI features.

Both offer exposure to your favored sectors without excessive volatility.

============================================================
Stored Memories in tmp/user_memory.json:
============================================================
  • User is interested in AI and semiconductor stocks.
  • User has a moderate risk tolerance.

✅ Done! The agent learned your preferences and used them.
"""
