from pathlib import Path
from agno.agent import Agent
from agno.models.google import Gemini
from agno.skills import Skills, LocalSkills

# Load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Load the generated Skills from the local directory
# ---------------------------------------------------------------------------
# Path to the root 'skills' folder
skills_path = Path.cwd() / "skills"

# Initialize the Skills object with the LocalSkills loader
agent_skills = Skills(
    loaders=[
        LocalSkills(path=str(skills_path))
    ]
)

# ---------------------------------------------------------------------------
# Define the Playable Agent
# ---------------------------------------------------------------------------
optimizer_agent = Agent(
    name="SQL Optimization Assistant",
    model=Gemini(id="gemini-2.0-flash-001"),
    skills=agent_skills,
    instructions=[
        "You are an AI assistant that uses the 'SQL Optimizer' skill to help users.",
        "Always refer to the SKILL.md for instructions and use the scripts/ in the skill if needed.",
        "You have access to a SQL optimization cheatsheet in the skill references.",
    ],
    markdown=True,
)

# ---------------------------------------------------------------------------
# Demonstrate the Agent 'playing' the skill
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Test query that needs optimization
    slow_query = """
    SELECT u.name, o.total_amount
    FROM users u
    JOIN orders o ON u.id = o.user_id
    WHERE u.id = 123;
    """
    
    # Example EXPLAIN plan
    explain_plan = """
    Nested Loop  (cost=4.63..1035.79 rows=1 width=113) (actual time=0.045..0.048 rows=1 loops=1)
      ->  Seq Scan on users  (cost=0.00..32.40 rows=1 width=37) (actual time=0.015..0.017 rows=1 loops=1)
            Filter: (id = 123)
      ->  Index Scan using orders_user_id_idx on orders  (cost=0.29..8.30 rows=1 width=76) (actual time=0.024..0.025 rows=1 loops=1)
            Index Cond: (user_id = users.id)
    """

    print("\n--- SQL Optimizer Agent Demo ---\n")
    optimizer_agent.print_response(
        f"Please analyze and optimize this query:\n\n{slow_query}\n\nHere is the execution plan:\n{explain_plan}",
        stream=True,
    )
