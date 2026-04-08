from pathlib import Path
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.bravesearch import BraveSearchTools
from agno.tools.file import FileTools
from agno.workflow import Step, Workflow

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ROOT_DIR = Path.cwd()
SKILLS_DIR = ROOT_DIR / "skills"

# ---------------------------------------------------------------------------
# Setup Tools
# ---------------------------------------------------------------------------
# We use BraveSearch for research as requested
# Handle both BRAVE_API_KEY and BRAVE_SEARCH_API_KEY
import os
brave_key = os.getenv("BRAVE_API_KEY") or os.getenv("BRAVE_SEARCH_API_KEY")
search_tools = BraveSearchTools(api_key=brave_key)

# We use FileTools to save the generated skill files
# We limit it to the skills directory for safety
file_tools = FileTools(base_dir=SKILLS_DIR)

# ---------------------------------------------------------------------------
# Step 1: Research Agent — Finds best practices and standards
# ---------------------------------------------------------------------------
research_agent = Agent(
    name="Skill Researcher",
    model=Gemini(id="gemini-1.5-flash"),
    tools=[search_tools],
    instructions=[
        "You are an expert technical researcher.",
        "Your goal is to find the 'golden standards' and best practices for a specific AI skill.",
        "Search for:",
        "1. Core concepts and definitions.",
        "2. Common workflows and step-by-step guides.",
        "3. Recommended tools, libraries, or patterns.",
        "4. Common pitfalls and anti-patterns to avoid.",
        "Provide a detailed research report focused on how an AI agent should perform this skill.",
    ],
)

research_step = Step(
    name="Researching Skill Standards",
    agent=research_agent,
    description="Research best practices and industry standards for the skill",
)

# ---------------------------------------------------------------------------
# Step 1.5: Delay Step — Avoid rate limits on Free Tier
# ---------------------------------------------------------------------------
def delay_executor(step_input):
    import time
    logger.info("Waiting 65 seconds to avoid Gemini rate limits...")
    time.sleep(65)
    return step_input.input # Pass research report through

delay_step = Step(
    name="Wait for Quota",
    executor=delay_executor,
    description="Wait for 20 seconds to avoid rate limits",
)

# ---------------------------------------------------------------------------
# Step 2: Developer Agent — Generates the skill files
# ---------------------------------------------------------------------------
developer_agent = Agent(
    name="Skill Developer",
    model=Gemini(id="gemini-1.5-flash"),
    tools=[file_tools],
    instructions=[
        "You are a Senior AI Engineer specializing in Agno Skill development.",
        "Your task is to take a research report and generate a complete, production-ready 'Skill' for an Agno Agent.",
        "",
        "A Skill must consist of three components:",
        "1. SKILL.md: Instructions for the agent. Must include YAML frontmatter with 'name' and 'description'.",
        "2. scripts/: Executable Python scripts that implement core logic or tools for the skill.",
        "3. references/: Documentation, cheat sheets, or pattern guides.",
        "",
        "STRICT REQUIREMENTS:",
        "- All files must be saved relative to the skill directory (e.g. 'sql_optimizer/SKILL.md').",
        "- The instructions must be concise but detailed, focusing on actionable steps for an AI agent.",
        "- Scripts should be modular, well-commented, and follow Python best practices.",
        "- Use the `save_file` tool to write each file to the filesystem.",
        "",
        "DIR STRUCTURE:",
        "<skill_name>/SKILL.md",
        "<skill_name>/scripts/<script_name>.py",
        "<skill_name>/references/<ref_name>.md",
    ],
)

developer_step = Step(
    name="Generating Skill Files",
    agent=developer_agent,
    description="Generate SKILL.md, scripts, and references based on research",
)

# ---------------------------------------------------------------------------
# Create the Skill Creator Workflow
# ---------------------------------------------------------------------------
skill_creator = Workflow(
    name="Skill Creator Workflow",
    description="Automated pipeline to research and generate high-quality Agno Skills",
    steps=[
        research_step,
        delay_step,
        developer_step,
    ],
)

# ---------------------------------------------------------------------------
# CLI Execution
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import asyncio
    
    # Example: Create a SQL Optimizer skill
    skill_creator.print_response(
        "Create a 'SQL Optimizer' skill. It should help agents analyze slow queries, "
        "suggest indexes, and rewrite queries for better performance in PostgreSQL.",
        stream=True,
    )
