"""
🍳 MTP Cookbook — Recipe 03: Using Built-in Toolkits
=====================================================
MTP ships with ready-to-use toolkits. This recipe also shows how to
replace built-in toolkits with custom @mtp_tool functions when the
built-in causes planning/async errors with certain models.

What you'll learn:
- Registering built-in toolkits with the correct namespace
- Writing lightweight @mtp_tool replacements for reliability
- Combining multiple tools in one agent
- Letting the agent pick the right tool automatically

⚠️  Namespace matters!
    The first argument of register_toolkit_loader() MUST match the
    toolkit's internal namespace exactly:

    CalculatorToolkit → "calculator"
    ShellToolkit      → "shell"
    WikipediaToolkit  → "wikipedia"
    FileToolkit       → "file"
    WebsiteToolkit    → "website"

⚠️  Known issue with free/small models:
    Some models generate $ref IDs that don't match MTP's execution plan,
    causing PlanValidationError. The custom @mtp_tool approach below
    avoids this entirely by removing the planning layer.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/00_quickstart/03_builtin_toolkits.py
"""

import math
import os
from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Step 1: Define reliable custom tools (no planning layer = no ref errors)
# ---------------------------------------------------------------------------
# These replace CalculatorToolkit and ShellToolkit with simple @mtp_tool
# functions that execute directly — compatible with all models.

@mtp_tool(description=(
    "Evaluate a mathematical expression and return the result. "
    "Supports +, -, *, /, **, sqrt, and standard Python math."
))
def calculate(expression: str) -> str:
    """
    Safely evaluates a math expression using Python's math module.
    Example: calculate("(45 * 12) + 120") → "660"
    """
    try:
        # Allow safe math functions only
        allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        result = eval(expression, {"__builtins__": {}}, allowed)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Error evaluating expression: {e}"


@mtp_tool(description=(
    "List the files and folders in a given directory path. "
    "Use '.' for the current directory."
))
def list_files(directory: str = ".") -> str:
    """
    Lists files and folders in the given directory.
    Example: list_files(".") → "01_hello.py\n02_tool.py\n..."
    """
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
# Note: we use MTPAgent with toolkit_from_functions just like Recipe 02
travel_kit = Agent.toolkit_from_functions("system", calculate, list_files)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("system", travel_kit)

# We use a stable free model from OpenRouter
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
    print("  MTP Cookbook — 03: Built-in Toolkits (Custom Fallback)")
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
    print("✅ Done! Next: see 04_streaming.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
