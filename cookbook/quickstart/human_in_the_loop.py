"""
🍳 MTP Cookbook — Human in the Loop
================================================
This example shows how to require user confirmation before executing
certain tools. Critical for actions that are irreversible or sensitive.

We'll build on our self-learning agent, and ask for user confirmation 
before saving a learning to the database.

Key concepts:
- MTP runs tools synchronously, so we can use standard Python `input()`
  inside our tools to pause execution and ask the user for confirmation.
- If the user denies it, the tool can return an error string to the Agent,
  and the Agent will handle the rejection gracefully.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/human_in_the_loop.py
"""

from datetime import datetime, timezone
from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter
from mtp.session_store import JsonSessionStore

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Custom Tool: Save Learning (Requires Confirmation via Input)
# ---------------------------------------------------------------------------
@mtp_tool(description="Save an important insight. This will prompt the user for confirmation.")
def save_learning(title: str, learning: str) -> str:
    """
    Save a reusable insight to the knowledge base for future reference.
    This action requires user confirmation before executing.

    Args:
        title: Short descriptive title (e.g., "Tech stock P/E benchmarks")
        learning: The insight to save — be specific and actionable
    """
    print("\n" + "=" * 40)
    print("⚠️  HUMAN-IN-THE-LOOP INTERVENTION ⚠️")
    print("=" * 40)
    print(f"The Agent wants to save the following learning:\n")
    print(f"Title: {title}")
    print(f"Content: {learning}\n")
    
    # Prompt the user for confirmation!
    choice = input("Do you approve this action? (y/n): ").strip().lower()
    print("=" * 40 + "\n")
    
    if choice != "y":
        return "Action rejected by the user. Do not proceed with saving this."

    # If approved, proceed with the actual action
    saved_time = datetime.now(timezone.utc).isoformat()
    return f"Successfully saved: '{title}' at {saved_time}."


@mtp_tool(description="Get market data for a stock.")
def get_market_data(ticker: str) -> str:
    """Returns simulated financial data."""
    return f"Simulated data for {ticker}: Tech stocks currently average a 25-35 P/E ratio."

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
instructions = """\
You are a Finance Agent that learns and improves over time.

## Workflow
1. Gather Information
   - Use the `get_market_data` tool if needed.

2. Propose Learnings
   - After answering the user, consider if there is a reusable insight.
   - If there is, immediately call `save_learning` to save it.
   - The user will be prompted to approve the action in their terminal.

## What Makes a Good Learning
- Specific: "Tech P/E ratios typically range 20-35x"
- Actionable: Can be applied to future questions
"""

# ---------------------------------------------------------------------------
# Create the Agent
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

hitl_kit = Agent.toolkit_from_functions(
    "hitl_tools",
    save_learning,
    get_market_data
)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("core", hitl_kit)

agent_store = JsonSessionStore(db_path="tmp/hitl_sessions")

human_in_the_loop_agent = Agent.MTPAgent(
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
    print("  MTP Cookbook — Human in the Loop")
    print("=" * 60)

    # Ask a question that will trigger the agent to learn and save
    prompt = "What's a healthy P/E ratio for tech stocks? Please save that insight."
    print(f"\n[User]: {prompt}")
    print("-" * 30)
    
    # Run the agent. The execution will pause mid-way when the agent calls the tool!
    response = human_in_the_loop_agent.run(prompt, session_id="hitl-session-1")
    
    print(f"\nAgent Final Response:\n{response}")

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Human in the Loop
============================================================

[User]: What's a healthy P/E ratio for tech stocks? Please save that insight.
------------------------------

========================================
⚠️  HUMAN-IN-THE-LOOP INTERVENTION ⚠️
========================================
The Agent wants to save the following learning:

Title: Healthy Tech P/E Ratio
Content: Tech stocks currently average a 25-35 P/E ratio.

Do you approve this action? (y/n): y
========================================

Agent Final Response:
Based on current market data, a healthy P/E ratio for tech stocks averages around 25 to 35. This reflects the growth premium often associated with the sector. 

I have successfully saved this insight for future reference!
"""
