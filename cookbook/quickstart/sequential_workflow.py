"""
🍳 MTP Cookbook — Sequential Workflow
============================================
This example shows how to chain multiple agents together in a sequence,
where the output of one agent becomes the input for the next.

We'll build a Content Creation Pipeline:
1. Researcher: Gathers information and writes bullet points
2. Writer: Takes the bullet points and writes a cohesive article
3. Reviewer: Checks the article for tone and formatting

Key concepts:
- Sequential flow: Using Python to pass `run().final_text` from one agent to the next
- specialized agents: Each agent has a distinct instruction set

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/sequential_workflow.py
"""

from mtp import Agent, mtp_tool, toolkit_from_functions, ToolRegistry
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()

provider = OpenRouter(model="openai/gpt-oss-120b:free")

# ---------------------------------------------------------------------------
# Simple Mock Tool
# ---------------------------------------------------------------------------
@mtp_tool(description="Search the web for information about a topic.")
def web_search(query: str) -> str:
    db = {
        "NVDA": "NVIDIA is dominating the AI chip market. Their new Blackwell architecture is highly anticipated.",
        "AMD": "AMD is gaining ground in the datacenter market and launching competitive AI accelerators.",
    }
    for key, value in db.items():
        if key in query.upper():
            return value
    return f"Found generic information about {query}: It's a trending topic."

tools = ToolRegistry()
tools.register_toolkit_loader("core", toolkit_from_functions("web", web_search))

# ---------------------------------------------------------------------------
# Agent 1: The Researcher
# ---------------------------------------------------------------------------
researcher = Agent(
    provider=provider,
    tools=tools,
    instructions="""\
You are an expert researcher. Given a topic, use the web_search tool to find information.
Your output MUST be a concise bulleted list of facts. Do not write full paragraphs.
""",
)

# ---------------------------------------------------------------------------
# Agent 2: The Writer
# ---------------------------------------------------------------------------
writer = Agent(
    provider=provider,
    tools=ToolRegistry(),  # The writer doesn't need search tools, just instructions
    instructions="""\
You are a professional content writer. You will be given a list of bullet points.
Your job is to turn those points into a well-written, engaging short article (2-3 paragraphs).
Use a confident, informative tone.
""",
)

# ---------------------------------------------------------------------------
# Agent 3: The Reviewer
# ---------------------------------------------------------------------------
reviewer = Agent(
    provider=provider,
    tools=ToolRegistry(),  # The reviewer doesn't need tools
    instructions="""\
You are a strict editor. Review the provided article.
Make sure it has a catchy title, good flow, and no grammatical errors.
Return ONLY the finalized, polished article.
""",
)

# ---------------------------------------------------------------------------
# Run Sequential Workflow
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("  MTP Cookbook — Sequential Workflow")
    print("=" * 60)

    topic = "NVDA and AMD AI chips"
    print(f"Target Topic: {topic}\n")

    # Step 1: Research
    print("🔍 [1/3] Researcher is gathering information...")
    research_output = researcher.run(f"Research: {topic}")
    print(f"--- Research Results ---\n{research_output}\n")

    # Step 2: Write
    print("✍️ [2/3] Writer is drafting the article...")
    draft_output = writer.run(f"Write an article based on these facts:\n{research_output}")
    print(f"--- Draft Article ---\n{draft_output}\n")

    # Step 3: Review
    print("✅ [3/3] Reviewer is polishing the final content...")
    final_output = reviewer.run(f"Review and polish this article:\n{draft_output}")
    
    print("=" * 60)
    print("  FINAL PUBLISHED ARTICLE")
    print("=" * 60)
    print(final_output)

if __name__ == "__main__":
    main()
