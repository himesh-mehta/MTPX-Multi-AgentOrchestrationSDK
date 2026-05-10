"""
🍳 MTP Cookbook — Agent with Tools
=====================================================
Agents are powerful because they can use tools to interact with
the outside world. This recipe shows how to define and use tools.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_tools.py
"""

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Step 1: Define your custom tools
# ---------------------------------------------------------------------------

@mtp_tool(description="Get the current weather for a given city")
def get_weather(location: str) -> str:
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
provider = OpenRouter(model="openai/gpt-oss-120b:free")

travel_kit = Agent.toolkit_from_functions("travel", get_weather, convert_currency)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("travel", travel_kit)

agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=(
        "You are a helpful travel assistant. "
        "Use the provided tools to answer the user's questions about weather and currency."
    ),
)

# ---------------------------------------------------------------------------
# Step 3: Run the agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 55)
    print("  MTP Cookbook — Agent with Tools")
    print("=" * 55)

    print("\n[Query 1] Weather tool")
    print("-" * 30)
    response = agent.run("What is the weather like in Mumbai today?")
    print(f"Agent: {response}")

    print("\n[Query 2] Currency tool")
    print("-" * 30)
    response = agent.run("How much is 5000 INR in USD?")
    print(f"Agent: {response}")

    print("\n[Query 3] Both tools in one prompt")
    print("-" * 30)
    response = agent.run("I am traveling from Tokyo to Paris. What is the weather in Paris and how much is 10000 JPY in EUR?")
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
  MTP Cookbook — Agent with Tools
=======================================================

[Query 1] Weather tool
------------------------------
Agent: The weather in Mumbai is currently **hot and humid**, with a temperature of **34°C** and **partly cloudy** skies. Stay hydrated and carry an umbrella if you're heading out!

[Query 2] Currency tool
------------------------------
Agent: **5,000 INR** is equivalent to **60.00 USD** at the current exchange rate. 

Is there anything else you'd like to know? 😊
                                            
[Query 3] Both tools in one prompt
------------------------------    
                              
Agent: Here's everything you need for your trip from Tokyo to Paris:

- **Paris Weather:** ☀️ **Sunny**, with a pleasant temperature of **22°C** and a **light breeze**. Great weather for exploring the city!
- **Currency Conversion:** **10,000 JPY** = **62.04 EUR** at the current exchange rate.

Enjoy your trip to Paris! 🗼 Is there anything else you'd like to know?

=======================================================
✅ Done! Next: explore other agents in this directory.
=======================================================
"""
