"""
🍳 MTP Cookbook — Agent with Structured Output
=====================================================
This example shows how to get structured, typed responses from your agent.
Instead of free-form text, we instruct the agent to output JSON that matches
a Pydantic model we can trust.

Perfect for building pipelines, UIs, or integrations where you need
predictable data shapes. Parse it, store it, display it — no regex required.

Prerequisites:
    pip install mtp python-dotenv pydantic

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_structured_output.py
"""

import json
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# Structured Output Schema
# ---------------------------------------------------------------------------
class StockAnalysis(BaseModel):
    """Structured output for stock analysis."""

    ticker: str = Field(..., description="Stock ticker symbol (e.g., NVDA)")
    company_name: str = Field(..., description="Full company name")
    current_price: float = Field(..., description="Current stock price in USD")
    market_cap: str = Field(..., description="Market cap (e.g., '3.2T' or '150B')")
    pe_ratio: Optional[float] = Field(None, description="P/E ratio, if available")
    week_52_high: float = Field(..., description="52-week high price")
    week_52_low: float = Field(..., description="52-week low price")
    summary: str = Field(..., description="One-line summary of the stock")
    key_drivers: List[str] = Field(..., description="2-3 key growth drivers")
    key_risks: List[str] = Field(..., description="2-3 key risks")
    recommendation: str = Field(
        ..., description="One of: Strong Buy, Buy, Hold, Sell, Strong Sell"
    )

# ---------------------------------------------------------------------------
# Tools Configuration
# ---------------------------------------------------------------------------
# Since we don't have YFinanceTools built-in, we simulate a robust finance tool
@mtp_tool(description="Get detailed stock market data for a given ticker symbol.")
def get_stock_data(ticker: str) -> str:
    # Simulated data for demonstration
    db = {
        "NVDA": {
            "name": "NVIDIA Corporation",
            "price": 187.90,
            "market_cap": "4.6T",
            "pe_ratio": 45.5,
            "52_low": 75.60,
            "52_high": 195.95,
        },
        "TSLA": {
            "name": "Tesla, Inc.",
            "price": 312.45,
            "market_cap": "995B",
            "pe_ratio": 65.2,
            "52_low": 138.80,
            "52_high": 348.30,
        }
    }
    t = ticker.upper()
    if t in db:
        return json.dumps(db[t])
    return f"Data for {ticker} not found."

# ---------------------------------------------------------------------------
# Agent Instructions
# ---------------------------------------------------------------------------
schema_json = StockAnalysis.model_json_schema()

instructions = f"""\
You are a Finance Agent — a data-driven analyst who retrieves market data,
computes key ratios, and produces concise, decision-ready insights.

## Workflow
1. Retrieve: Use the `get_stock_data` tool to fetch price, market cap, P/E, 52-week range.
2. Analyze: Identify 2-3 key drivers and 2-3 key risks based on standard industry knowledge.
3. Recommend: Provide a decisive recommendation (Strong Buy, Buy, Hold, Sell, Strong Sell).

## Structured Output Rules
You MUST return ONLY a raw JSON object matching this JSON schema:
{json.dumps(schema_json, indent=2)}

Do NOT wrap the JSON in Markdown code blocks (like ```json). Just output the raw JSON string.
"""

# ---------------------------------------------------------------------------
# Create the Agent
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

finance_kit = Agent.toolkit_from_functions("finance", get_stock_data)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("finance", finance_kit)

agent_with_structured_output = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=instructions,
)

# ---------------------------------------------------------------------------
# Run the Agent
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Agent with Structured Output")
    print("=" * 60)

    print("\n[User]: Analyze NVIDIA")
    print("-" * 30)
    
    # Run the agent
    response_text = agent_with_structured_output.run("Analyze NVDA")
    
    # Parse the structured output
    try:
        # Sometimes models still add markdown blocks despite instructions
        clean_json = response_text.replace("```json", "").replace("```", "").strip()
        analysis = StockAnalysis.model_validate_json(clean_json)
        
        # Use it programmatically
        print(f"\nStock Analysis: {analysis.company_name} ({analysis.ticker})")
        print("-" * 60)
        print(f"Price: ${analysis.current_price:.2f}")
        print(f"Market Cap: {analysis.market_cap}")
        print(f"P/E Ratio: {analysis.pe_ratio or 'N/A'}")
        print(f"52-Week Range: ${analysis.week_52_low:.2f} - ${analysis.week_52_high:.2f}")
        print(f"\nSummary: {analysis.summary}")
        print("\nKey Drivers:")
        for driver in analysis.key_drivers:
            print(f"  • {driver}")
        print("\nKey Risks:")
        for risk in analysis.key_risks:
            print(f"  • {risk}")
        print(f"\nRecommendation: {analysis.recommendation}")
        print("=" * 60)
        
    except ValidationError as e:
        print(f"Failed to parse structured output:\n{e}")
        print(f"Raw output was:\n{response_text}")

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Agent with Structured Output
============================================================

[User]: Analyze NVIDIA
------------------------------

Stock Analysis: NVIDIA Corporation (NVDA)
------------------------------------------------------------
Price: $187.90
Market Cap: 4.6T
P/E Ratio: 45.5
52-Week Range: $75.60 - $195.95

Summary: Dominant market leader in AI accelerators experiencing explosive revenue growth.

Key Drivers:
  • Massive and sustained enterprise demand for Hopper and Blackwell GPUs.
  • Unmatched software ecosystem (CUDA) creating high switching costs.
  • Rapidly expanding into sovereign AI and networking infrastructure.

Key Risks:
  • High expectations baked into valuation, leaving little room for misexecution.
  • Increasing competition from custom silicon (ASICs) developed by major cloud providers.
  • Geopolitical risks regarding chip export restrictions.

Recommendation: Buy
============================================================
"""
