"\"\"
🍳 MTP Cookbook — Basic Agent
=====================================================
The simplest way to use MTP. We initialize an agent and ask it a question.

Prerequisites:
    pip install mtp python-dotenv

Setup:
    OPENROUTER_API_KEY=your_key_here in .env

Run:
    python cookbook/quickstart/basic_agent.py
\"\""

from mtp import Agent
from mtp.providers import OpenRouter

Agent.load_dotenv_if_available()
provider = OpenRouter(model="openai/gpt-oss-120b:free")

agent = Agent.MTPAgent(
    provider=provider,
    tools=Agent.ToolRegistry(),
    instructions="You are a helpful and concise assistant."
)

def main():
    print("==================================================")
    print("  MTP Cookbook — Basic Agent")
    print("==================================================")
    
    prompt = "Explain what a 'Model Tool Protocol' might be in one short paragraph."
    response = agent.run(prompt)
    print(f"\n[User]: {prompt}\n")
    print(f"Agent: {response}")

if __name__ == "__main__":
    main()
