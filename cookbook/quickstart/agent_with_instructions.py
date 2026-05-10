"""
🍳 MTP Cookbook — Agent with Instructions
=====================================================
You can customize your agent's personality and behavior by
passing `instructions` when creating the agent.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_instructions.py
"""

from mtp import Agent
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Step 1: Create an agent with a specific persona
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

agent = Agent.MTPAgent(
    provider=provider,
    tools=Agent.ToolRegistry(),  # Empty registry since we don't need tools here
    instructions=(
        "You are Rohan, a senior software engineer and mentor from Bangalore, India. "
        "You are polite, extremely helpful, and explain technical concepts using clear, "
        "professional English. Keep your answers concise but informative."
    ),
)

# ---------------------------------------------------------------------------
# Step 2: Run the agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 55)
    print("  MTP Cookbook — Agent with Instructions")
    print("=" * 55)

    print("\n[User]: Hello! Can you tell me what a computer is?")
    print("-" * 30)
    response = agent.run("Hello! Can you tell me what a computer is?")
    print(f"Agent: {response}")

    print("\n[User]: What's the best way to learn Python programming?")
    print("-" * 30)
    response = agent.run("What's the best way to learn Python programming?")
    print(f"Agent: {response}")

    print("\n" + "=" * 55)
    print("✅ Done! Next: explore other agents in this directory.")
    print("=" * 55)

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
=======================================================
  MTP Cookbook — Agent with Instructions
=======================================================

[User]: Hello! Can you tell me what a computer is?
------------------------------
Agent: Hello! A computer is an electronic device that processes data according to a set of instructions called a program. It takes input, processes it using its central processing unit (CPU), and provides an output. Think of it as a highly efficient assistant that can perform complex calculations and manage information at lightning speed.

[User]: What's the best way to learn Python programming?
------------------------------
Agent: The best way to learn Python is through a mix of structured learning and hands-on practice. Here is a clear path you can follow:

1. **Grasp the Basics**: Start with fundamental concepts like variables, loops, and functions.
2. **Write Code Daily**: Consistency is key. Try solving small logical problems.
3. **Build Small Projects**: Apply what you learn by building simple applications, such as a to-do list.

Please let me know if you need any specific project ideas to get started!

=======================================================
✅ Done! Next: explore other agents in this directory.
=======================================================
"""
