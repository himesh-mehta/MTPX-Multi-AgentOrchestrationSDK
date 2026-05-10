"""
🍳 MTP Cookbook — Recipe 02: Creating a Custom Tool (Function)
===============================================================
Turn any Python function into a tool the model can call.

What you'll learn:
- Using the @mtp_tool decorator
- Registering a custom tool with ToolRegistry
- Letting the agent decide when to use your tool
- Returning structured data from tools

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/00_quickstart/02_custom_tool.py
"""

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Step 1: Define your custom tools using @mtp_tool
# ---------------------------------------------------------------------------
# The decorator exposes this function to the model.
# - description: tells the model WHEN to use this tool
# - type hints:  tell the model WHAT arguments to pass

@mtp_tool(description="Get the current weather for a given city")
def get_weather(location: str) -> str:
    """
    In a real app, call a weather API like OpenWeatherMap here.
    For this example we return a hardcoded response.
    """
    weather_data = {
        "paris":   "Sunny, 22°C, light breeze",
        "tokyo":   "Cloudy, 18°C, humidity 70%",
        "new york": "Rainy, 15°C, wind 20 km/h",
        "mumbai":  "Hot and humid, 34°C, partly cloudy",
    }
    key = location.lower()
    return weather_data.get(key, f"Weather data for '{location}' is unavailable.")


@mtp_tool(description="Convert an amount from one currency to another")
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Hardcoded exchange rates for demo purposes.
    Replace with a real forex API in production.
    """
    rates_to_usd = {"USD": 1.0, "EUR": 1.08, "INR": 0.012, "JPY": 0.0067}
    f = from_currency.upper()
    t = to_currency.upper()
    if f not in rates_to_usd or t not in rates_to_usd:
        return f"Unsupported currency pair: {f} → {t}"
    converted = amount * rates_to_usd[f] / rates_to_usd[t]
    return f"{amount} {f} = {converted:.2f} {t}"


# ---------------------------------------------------------------------------
# Step 2: Build the agent and register tools
# ---------------------------------------------------------------------------
provider = OpenRouter(model="inclusionai/ring-2.6-1t:free")

# Create a toolkit from our custom functions
# This is the cleanest way to add tools to MTPAgent
travel_kit = Agent.toolkit_from_functions("travel", get_weather, convert_currency)

# Add the toolkit to the registry
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("travel", travel_kit)

# Initialize the agent with the populated registry
agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions="You are a helpful travel assistant. Use tools to answer accurately.",
)


# ---------------------------------------------------------------------------
# Step 3: Run prompts that trigger the tools
# ---------------------------------------------------------------------------
def main():
    print("=" * 55)
    print("  MTP Cookbook — 02: Custom Tool")
    print("=" * 55)

    print("\n[Query 1] Weather tool")
    print("-" * 30)
    response = agent.run("What's the weather like in Mumbai?")
    print(f"Agent: {response}")

    print("\n[Query 2] Currency tool")
    print("-" * 30)
    response = agent.run("Convert 5000 INR to USD.")
    print(f"Agent: {response}")

    print("\n[Query 3] Both tools in one prompt")
    print("-" * 30)
    response = agent.run(
        "I'm travelling from Tokyo to Paris. What's the weather there "
        "and how much is 10000 JPY in EUR?"
    )
    print(f"Agent: {response}")

    print("\n" + "=" * 55)
    print("✅ Done! Next: see 03_builtin_toolkits.py")
    print("=" * 55)


if __name__ == "__main__":
    main()
