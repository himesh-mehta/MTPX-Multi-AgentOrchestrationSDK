"""
🍳 MTP Cookbook — Agent with Typed Input & Output
=====================================================
When building APIs, type safety is critical for both the request
and the response. This recipe demonstrates how an agent can enforce
strict Pydantic schemas on both ends.

What you'll learn:
- Defining an input schema
- Processing input via the agent using the schema
- Generating a matching output schema

Prerequisites:
    pip install mtp python-dotenv pydantic

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/agent_with_typed_input_output.py
"""

import json
from typing import List, Optional
from pydantic import BaseModel, Field

from mtp import Agent, mtp_tool
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

# ---------------------------------------------------------------------------
# 1. Typed Input Schema
# ---------------------------------------------------------------------------
class AnalysisRequest(BaseModel):
    ticker: str = Field(..., description="Stock symbol to analyze")
    include_risks: bool = Field(default=False, description="Whether to include risks")
    analysis_depth: str = Field(default="quick", description="Depth: 'quick' or 'deep'")

# ---------------------------------------------------------------------------
# 2. Typed Output Schema
# ---------------------------------------------------------------------------
class AnalysisResponse(BaseModel):
    ticker: str
    company_name: str
    summary: str
    key_drivers: List[str]
    key_risks: Optional[List[str]] = Field(default=None)
    recommendation: str

# ---------------------------------------------------------------------------
# 3. Simulate Market Data Tool
# ---------------------------------------------------------------------------
@mtp_tool(description="Get market data for a ticker")
def get_market_data(ticker: str) -> str:
    db = {
        "AAPL": {"name": "Apple Inc.", "price": 175.50},
        "NVDA": {"name": "NVIDIA Corp.", "price": 187.90}
    }
    t = ticker.upper()
    return json.dumps(db.get(t, {"name": "Unknown", "price": 0.0}))

# ---------------------------------------------------------------------------
# 4. Create the Agent
# ---------------------------------------------------------------------------
provider = OpenRouter(model="openai/gpt-oss-120b:free")

market_kit = Agent.toolkit_from_functions("market", get_market_data)
tools = Agent.ToolRegistry()
tools.register_toolkit_loader("market", market_kit)

# Pass the schema logic via instructions so the LLM respects it
in_schema = AnalysisRequest.model_json_schema()
out_schema = AnalysisResponse.model_json_schema()

instructions = f"""\
You are a strict API agent.
You will receive an `AnalysisRequest` JSON object representing the user's input.
You must fetch the market data using the tool and then output an `AnalysisResponse` JSON object.

Input Schema format (you will receive this):
{json.dumps(in_schema, indent=2)}

Output Schema format (you MUST output this):
{json.dumps(out_schema, indent=2)}

Rule: If include_risks is false, leave key_risks as null.
Do NOT output markdown blocks. Just output raw JSON matching the Output Schema.
"""

agent = Agent.MTPAgent(
    provider=provider,
    tools=tools,
    instructions=instructions,
)

# ---------------------------------------------------------------------------
# 5. Helper wrapper for typed API
# ---------------------------------------------------------------------------
def run_typed_analysis(request: AnalysisRequest) -> AnalysisResponse:
    # Convert typed input to JSON string
    prompt = request.model_dump_json()
    
    # Run the agent
    response_text = agent.run(prompt)
    
    # Parse output back to typed Pydantic object
    clean_json = response_text.replace("```json", "").replace("```", "").strip()
    return AnalysisResponse.model_validate_json(clean_json)

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Typed Input/Output")
    print("=" * 60)

    # Test Case 1: Deep Analysis with Risks
    req1 = AnalysisRequest(ticker="NVDA", include_risks=True, analysis_depth="deep")
    print(f"\n[Request 1]: {req1.model_dump_json(indent=2)}")
    print("-" * 30)
    
    res1 = run_typed_analysis(req1)
    print(f"Parsed Response Type: {type(res1)}")
    print(f"Company: {res1.company_name}")
    print(f"Risks Included: {bool(res1.key_risks)}")
    if res1.key_risks:
        for r in res1.key_risks:
            print(f"  • {r}")

    # Test Case 2: Quick Analysis without Risks
    req2 = AnalysisRequest(ticker="AAPL", include_risks=False, analysis_depth="quick")
    print(f"\n[Request 2]: {req2.model_dump_json(indent=2)}")
    print("-" * 30)
    
    res2 = run_typed_analysis(req2)
    print(f"Parsed Response Type: {type(res2)}")
    print(f"Company: {res2.company_name}")
    print(f"Risks Included: {bool(res2.key_risks)}")

    print("\n" + "=" * 60)
    print("✅ Done! Next: Check out agent storage.")
    print("=" * 60)

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Typed Input/Output
============================================================

[Request 1]: {
  "ticker": "NVDA",
  "include_risks": true,
  "analysis_depth": "deep"
}
------------------------------
Parsed Response Type: <class '__main__.AnalysisResponse'>
Company: NVIDIA Corp.
Risks Included: True
  • Potential market saturation
  • Supply chain dependencies

[Request 2]: {
  "ticker": "AAPL",
  "include_risks": false,
  "analysis_depth": "quick"
}
------------------------------
Parsed Response Type: <class '__main__.AnalysisResponse'>
Company: Apple Inc.
Risks Included: False

============================================================
✅ Done! Next: Check out agent storage.
============================================================
"""
