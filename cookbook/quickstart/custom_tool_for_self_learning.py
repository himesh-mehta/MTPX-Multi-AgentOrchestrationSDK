"""
🍳 MTP Cookbook — Custom Tool for Self-Learning
=====================================================
This example shows how to write custom tools for your agent.
A tool is just a Python function — the agent calls it when needed.

We'll build a self-learning agent that can save insights to a knowledge base.
The key concept: any function can become a tool.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/custom_tool_for_self_learning.py
"""

import json
import os
from datetime import datetime, timezone

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter
from mtp.session_store import JsonSessionStore

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Simple Knowledge Base for Learnings
# ---------------------------------------------------------------------------
class LearningsDB:
    def __init__(self, file_path="tmp/learnings.json"):
        self.file_path = file_path
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    self.db = json.load(f)
            except Exception:
                self.db = {}
        else:
            self.db = {}

    def save(self, title: str, payload: dict):
        self.db[title] = payload
        os.makedirs(os.path.dirname(self.file_path) or ".", exist_ok=True)
        with open(self.file_path, "w") as f:
            json.dump(self.db, f, indent=2)

    def get_all(self):
        return self.db

learnings_db = LearningsDB()

# ---------------------------------------------------------------------------
# Custom Tools
# ---------------------------------------------------------------------------
@mtp_tool(description="Save a reusable insight to the knowledge base for future reference.")
def save_learning(title: str, learning: str) -> str:
    """
    Save a reusable insight.
    Args:
        title: Short descriptive title (e.g., "Tech stock P/E benchmarks")
        learning: The insight to save — be specific and actionable
    """
    if not title or not title.strip():
        return "Cannot save: title is required"
    if not learning or not learning.strip():
        return "Cannot save: learning content is required"

    payload = {
        "title": title.strip(),
        "learning": learning.strip(),
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    
    learnings_db.save(title, payload)
    return f"Successfully saved learning: '{title}'"

@mtp_tool(description="Search the knowledge base for previously saved learnings.")
def get_learnings() -> str:
    """Returns a list of all saved learnings and insights."""
    data = learnings_db.get_all()
    if not data:
        return "No learnings saved yet."
    
    result = "Saved Learnings:\n"
    for k, v in data.items():
        result += f"- **{k}**: {v['learning']}\n"
    return result

@mtp_tool(description="Get market data for a stock.")
def get_market_data(ticker: str) -> str:
    """Returns simulated financial data."""
    return f"Simulated data for {ticker}: Tech stocks currently average a 25-35 P/E ratio."

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a Finance Agent that learns and improves over time.

You have two special abilities:
1. Search your knowledge base for previously saved learnings using `get_learnings`.
2. Save new insights using the `save_learning` tool.

## Workflow

1. Check Knowledge First
   - Before answering, search for relevant prior learnings using `get_learnings`.
   - Apply any relevant insights to your response.

2. Gather Information
   - Use the `get_market_data` tool if needed.

3. Propose Learnings
   - After answering, consider: is there a reusable insight here?
   - If yes, propose it in this format at the end of your message:

---
**Proposed Learning**
Title: [concise title]
Learning: [the insight — specific and actionable]
Save this? (yes/no)
---

- ONLY call `save_learning` AFTER the user says "yes" or explicitly approves.
- If user says "no", acknowledge and move on.

## What Makes a Good Learning
- Specific: "Tech P/E ratios typically range 20-35x" not "P/E varies"
- Actionable: Can be applied to future questions
- Reusable: Useful beyond this one conversation
"""

# ---------------------------------------------------------------------------
# Create the Agent
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

learning_kit = Agent.toolkit_from_functions(
    "learning_tools",
    save_learning,
    get_learnings,
    get_market_data
)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("core", learning_kit)

agent_store = JsonSessionStore(db_path="tmp/learning_sessions")

self_learning_agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=instructions,
    session_store=agent_store,
)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Custom Tool for Self-Learning")
    print("=" * 60)

    session_id = "self-learning-session-1"

    # Turn 1: Ask a question that might produce a learning
    prompt1 = "What's a healthy P/E ratio for tech stocks?"
    print(f"\n[User]: {prompt1}")
    print("-" * 30)
    response = self_learning_agent.run(prompt1, session_id=session_id)
    print(f"Agent: {response}")

    # Turn 2: Approve the learning
    prompt2 = "yes"
    print(f"\n[User]: {prompt2}")
    print("-" * 30)
    response = self_learning_agent.run(prompt2, session_id=session_id)
    print(f"Agent: {response}")

    # Turn 3: Ask to retrieve learnings
    prompt3 = "What learnings do we have saved?"
    print(f"\n[User]: {prompt3}")
    print("-" * 30)
    response = self_learning_agent.run(prompt3, session_id=session_id)
    print(f"Agent: {response}")

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Custom Tool for Self-Learning
============================================================

[User]: What's a healthy P/E ratio for tech stocks?
------------------------------
Agent: Based on current market conditions, tech stocks typically average a P/E ratio between 25 and 35. This is generally higher than other sectors because investors are willing to pay a premium for expected future growth.

---
**Proposed Learning**
Title: Tech stock P/E benchmarks
Learning: Healthy P/E ratios for tech stocks typically range between 25x and 35x, reflecting growth premiums compared to other sectors.
Save this? (yes/no)
---

[User]: yes
------------------------------
Agent: Great! I have saved that insight to my knowledge base.

[User]: What learnings do we have saved?
------------------------------
Agent: Here are the learnings we have saved so far:

- **Tech stock P/E benchmarks**: Healthy P/E ratios for tech stocks typically range between 25x and 35x, reflecting growth premiums compared to other sectors.
"""
