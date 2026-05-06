from __future__ import annotations

from mtp import Agent, ToolRegistry, tool
from mtp.providers import Xiaomi


@tool("math.add", description="Add two numbers")
def add(a: float, b: float) -> float:
    return a + b


if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register(add)

    provider = Xiaomi(model="mimo-v2.5-pro")
    agent = Agent(provider=provider, tools=registry)

    result = agent.run_loop("Use the tool to add 19.5 and 22.5, then answer briefly.", max_rounds=2)
    print(result.final_text)
    print(result.usage)
