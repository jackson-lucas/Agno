from agno.agent.agent import Agent
from agno.models.openai import OpenAIChat

researcher = Agent(
    name="Researcher",
    model=OpenAIChat(id="gpt-4o"),
    instructions=["Research the given topic and provide a summary."],
    description="A helpful research assistant agent."
)
