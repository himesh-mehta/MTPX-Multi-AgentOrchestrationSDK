"""
🍳 MTP Cookbook — Multi-Agent Team
============================================
This example shows how to create a team of agents that work together.
Each agent has a specialized role, and the team leader coordinates.

We'll build an investment research team with opposing perspectives:
- Bull Agent: Makes the case FOR investing
- Bear Agent: Makes the case AGAINST investing
- Lead Analyst: Synthesizes into a balanced recommendation

This adversarial approach produces better analysis than a single agent.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/multi_agent_team.py
"""

from mtp import Agent, MTPAgent, ToolRegistry, toolkit_from_functions, mtp_tool
from mtp.providers import OpenRouter
from mtp.session_store import JsonSessionStore

Agent.load_dotenv_if_available()

provider = OpenRouter(model="openai/gpt-oss-120b:free")
session_store = JsonSessionStore(db_path="tmp/team_sessions")

# ---------------------------------------------------------------------------
# Simple Tool for the Analysts
# ---------------------------------------------------------------------------
@mtp_tool(description="Get financial metrics for a stock.")
def get_financials(ticker: str) -> str:
    db = {
        "NVDA": "P/E: 35. Growth: 120% YoY. Debt: Low. Margin: 75%.",
        "AMD": "P/E: 45. Growth: 50% YoY. Debt: Medium. Margin: 50%.",
    }
    return db.get(ticker.upper(), f"No data found for {ticker}")

finance_kit = toolkit_from_functions("finance", get_financials)
tools = ToolRegistry()
tools.register_toolkit_loader("core", finance_kit)

# ---------------------------------------------------------------------------
# Bull Agent — Makes the Case FOR
# ---------------------------------------------------------------------------
# Note: we use the base Agent class for members, as MTPAgent expects dict[str, Agent]
bull_agent = Agent(
    provider=provider,
    tools=tools,
    instructions="""\
You are a Bull Analyst. Your job is to make the strongest possible case
FOR investing in a stock. Find the positives:
- Growth drivers and catalysts
- Competitive advantages
- Strong financials and metrics

Be persuasive but grounded in data. Use the `get_financials` tool to get numbers.\
"""
)

# ---------------------------------------------------------------------------
# Bear Agent — Makes the Case AGAINST
# ---------------------------------------------------------------------------
bear_agent = Agent(
    provider=provider,
    tools=tools,
    instructions="""\
You are a Bear Analyst. Your job is to make the strongest possible case
AGAINST investing in a stock. Find the risks:
- Valuation concerns
- Competitive threats
- Weak spots in financials

Be critical but fair. Use the `get_financials` tool to get real numbers.\
"""
)

# ---------------------------------------------------------------------------
# Create Team Leader
# ---------------------------------------------------------------------------
leader_instructions = """\
You lead an investment research team with a Bull Analyst and a Bear Analyst.

## Process
1. Delegate to the 'bull_analyst' member to make the case FOR the stock.
2. Delegate to the 'bear_analyst' member to make the case AGAINST the stock.
3. Synthesize their arguments into a balanced recommendation.

## Output Format
After hearing from both analysts, provide:
- **Bull Case Summary**: Key points from the bull analyst
- **Bear Case Summary**: Key points from the bear analyst
- **Synthesis**: Where do they agree? Where do they disagree?
- **Recommendation**: Your balanced view (Buy/Hold/Sell) with confidence level.
"""

multi_agent_team = MTPAgent(
    provider=provider,
    tools=ToolRegistry(),  # Leader doesn't need finance tools, it uses members
    instructions=leader_instructions,
    members={
        "bull_analyst": bull_agent,
        "bear_analyst": bear_agent
    },
    mode="orchestration",
    session_store=session_store,
)

# ---------------------------------------------------------------------------
# Run Team
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Multi-Agent Team")
    print("=" * 60)

    session_id = "team-session-1"

    # First analysis
    prompt1 = "Should I invest in NVIDIA (NVDA)?"
    print(f"\n[User]: {prompt1}")
    print("-" * 30)
    response = multi_agent_team.run(prompt1, session_id=session_id)
    print(f"\n[Lead Analyst]:\n{response}")

    # Follow-up question — team remembers the previous analysis
    prompt2 = "How does AMD compare to that?"
    print(f"\n[User]: {prompt2}")
    print("-" * 30)
    response = multi_agent_team.run(prompt2, session_id=session_id)
    print(f"\n[Lead Analyst]:\n{response}")

if __name__ == "__main__":
    main()

# =============================================================================
# 📤 Output:
# =============================================================================
"""
============================================================
  MTP Cookbook — Multi-Agent Team
============================================================

[User]: Should I invest in NVIDIA (NVDA)?
------------------------------

[Lead Analyst]:
Here is the balanced investment research for NVIDIA (NVDA):

**Bull Case Summary**:
- **Strong Financials**: Exceptional 120% YoY growth with high profitability (75% margins).
- **Solid Foundation**: Low debt ensures financial stability.
- **Market Opportunity**: Capitalizing on massive AI hardware demand.

**Bear Case Summary**:
- **Valuation Concerns**: Trading at a high P/E ratio of 35, pricing in perfection.
- **Growth Sustainability**: Maintaining 120% YoY growth is extremely difficult long-term.
- **Concentration Risk**: Heavy reliance on a single high-margin sector (AI chips).

**Synthesis**:
Both analysts agree that NVDA's current performance is spectacular, driven by incredible 120% growth and 75% margins. The disagreement centers on whether this growth is sustainable enough to justify the premium 35 P/E ratio. The bull sees ongoing market dominance, while the bear sees a high bar for future earnings that could lead to a severe correction if missed.

**Recommendation**:
**Hold (Moderate Confidence)**
While the fundamental business is firing on all cylinders, the valuation leaves little room for error. Current investors should hold to capture ongoing AI momentum, but new money might want to wait for a broader market pullback to get a better entry point than the current 35x multiple.
"""
