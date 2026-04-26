from agno.workflow.workflow import Workflow
from agno.agent.agent import Agent
from agno.models.google import Gemini
from registry.agents.researcher import researcher

class ResearchWorkflow(Workflow):
    def run(self, topic: str):
        # Call the researcher agent
        response = researcher.run(f"Research {topic}")
        return response.content

# Instantiate the workflow
research_workflow = ResearchWorkflow(
    name="Research Workflow",
    description="A simple workflow that uses the Research Agent to summarize a topic."
)

# Export for the registry
components = [research_workflow]
