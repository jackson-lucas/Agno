from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.directus import DirectusTools
from dotenv import load_dotenv

load_dotenv()

# 1. Setup Directus Tools
# Note: Provide DIRECTUS_API_TOKEN in your environment or pass it here.
directus_tools = DirectusTools(
    url="http://localhost:8055",
)

# 2. Create an Agent with Directus capabilities
agent = Agent(
    name="Experiment Ledger Agent",
    model=Gemini(id="gemini-3-flash-preview"),
    instructions=[
        "You are an expert researcher managing an experimental ledger.",
        "You can create experiments, workflows, and tasks.",
        "When creating an experiment, remember to provide hypothesis, impact, confidence, and ease.",
        "When creating a task, ensure it links to either an experiment or a workflow.",
    ],
    tools=[directus_tools],
    markdown=True,
)

# 3. Example Usage
agent.print_response(
    "Create a new experiment with the hypothesis 'If we automate the ledger tracking, then we reduce manual errors by 30%'. "
    "Set impact: 8, confidence: 7, ease: 6. Then create a task for it: 'Setup Directus automation flow'.",
    stream=True,
)

# 4. List the experiments to verify
agent.print_response("What are the current experiments in the ledger?", stream=True)
