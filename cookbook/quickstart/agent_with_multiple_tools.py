"""
🍳 MTP Cookbook — Agent with Multiple Tools
=====================================================
MTP ships with ready-to-use toolkits. This recipe also shows how to
replace built-in toolkits with custom @mtp_tool functions when the
built-in causes planning/async errors with certain models.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_multiple_tools.py
"""

import math
import os
from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Step 1: Define reliable custom tools
# ---------------------------------------------------------------------------
@mtp_tool(description="Evaluate a mathematical expression and return the result.")
def calculate(expression: str) -> str:
    try:
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"

@mtp_tool(description="List the files and folders in a given directory path. Use '.' for the current directory.")
def list_files(directory: str = ".") -> str:
    try:
        entries = os.listdir(directory)
        if not entries:
            return f"Directory '{directory}' is empty."
        return "\n".join(sorted(entries))
    except FileNotFoundError:
        return f"Directory not found: '{directory}'"
    except PermissionError:
        return f"Permission denied: '{directory}'"

# ---------------------------------------------------------------------------
# Step 2: Register tools and build the agent
# ---------------------------------------------------------------------------
travel_kit = Agent.toolkit_from_functions("system", calculate, list_files)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("system", travel_kit)

provider = OpenRouter(model="openai/gpt-oss-120b:free")

agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=(
        "You are a precise assistant. "
        "Use the calculate tool for all math expressions. "
        "Use the list_files tool when asked about files or directories."
    ),
)

# ---------------------------------------------------------------------------
# Step 3: Run the agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 55)
    print("  MTP Cookbook — Agent with Multiple Tools")
    print("=" * 55)

    print("\n[Query 1] Calculator tool")
    print("-" * 30)
    response = agent.run("Calculate (45 * 12) + 120 and then divide by 7.")
    print(f"Agent: {response}")

    print("\n[Query 2] List files tool")
    print("-" * 30)
    response = agent.run("List the files in the current directory.")
    print(f"Agent: {response}")

    print("\n[Query 3] Combined")
    print("-" * 30)
    response = agent.run(
        "How many files are in the current directory? "
        "Also calculate 2 to the power of 10."
    )
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
  MTP Cookbook — Agent with Multiple Tools
=======================================================

[Query 1] Calculator tool
------------------------------
Agent: The result of ((45 * 12) + 120) divided by 7 is **approximately 94.29**.

[Query 2] List files tool
------------------------------
Agent: Here are the items in the current directory:

- `.env`
- `.git`
- `cookbook`
- `docs`
- `src`

[Query 3] Combined
------------------------------
Agent: - The current directory contains **19 items**.  
- 2^10 = 1024.

=======================================================
✅ Done! Next: explore other agents in this directory.
=======================================================
"""
