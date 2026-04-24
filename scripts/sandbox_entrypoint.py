import os
import sys
import json
from pathlib import Path

# Need to ensure we can import from agno if it's mounted, 
# but in the Dockerfile we `pip install agno`. However, to use the latest local code,
# it's usually better to just rely on the pip installed version unless we mount the libs.
# For this sandbox, we will rely on the pip installed version.

# We must be able to load from the mounted registry
from agno.registry.loader import RegistryLoader
from agno.agent.agent import Agent

def main():
    if len(sys.argv) < 2:
        print("Usage: python sandbox_entrypoint.py <path_to_manifest.json>")
        sys.exit(1)

    manifest_path = sys.argv[1]
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    task = manifest.get('task')
    if not task:
        print("No task specified in manifest!")
        sys.exit(1)

    print(f"--- Sandbox Execution Started ---")
    print(f"Task: {task}")
    
    # Load registry
    registry_path = Path("/registry")
    if not registry_path.exists():
        print("Error: /registry not mounted into the container.")
        sys.exit(1)
        
    print("Loading registry components...")
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()
    
    agent_ids = manifest.get('agent_ids', [])
    tool_ids = manifest.get('tool_ids', [])
    guardrail_ids = manifest.get('guardrail_ids', [])
    
    # 1. Resolve Agent
    agent = None
    if agent_ids:
        agent_name = agent_ids[0]
        for a in registry.agents:
            if getattr(a, "id", a.name) == agent_name or a.name == agent_name:
                agent = a
                break
    
    if not agent:
        # Fallback to a default agent if none is specified or found
        print("No specific agent found or specified. Using default Agent.")
        from agno.models.google import Gemini
        agent = Agent(name="DefaultSandboxAgent", model=Gemini(id="gemini-2.5-flash"))
    else:
        print(f"Using Agent: {agent.name}")

    # 2. Attach Tools
    tools_to_add = []
    for t_id in tool_ids:
        for t in registry.tools:
            if getattr(t, "name", None) == t_id:
                tools_to_add.append(t)
                print(f"Attached Tool: {t.name}")
                break
    
    if tools_to_add:
        # Agent.tools might be a list
        if agent.tools is None:
            agent.tools = []
        agent.tools.extend(tools_to_add)

    # 3. Guardrails (Not strictly implemented in Agno core as BaseGuardrail pre_hooks yet)
    # But we can simulate by calling them manually if they implement check()
    # For now, we will just print them.
    guardrails_to_add = []
    for g_id in guardrail_ids:
        for g in registry.guardrails:
            if getattr(g, "name", g.__class__.__name__) == g_id:
                guardrails_to_add.append(g)
                print(f"Active Guardrail: {g.name}")
                break
    
    # 4. Configure Observability
    print("Configuring Observability Bridge (PostgreSQL)...")
    try:
        from agno.db.postgres import PostgresDb
        from agno.tracing import setup_tracing
        db = PostgresDb(db_url="postgresql+psycopg://ai:ai@host.docker.internal:5532/ai")
        agent.db = db
        setup_tracing(db=db)
        agent.tracing = True
    except Exception as obs_err:
        print(f"Warning: Could not connect to Observability DB: {obs_err}")

    print("\nExecuting Task...")
    
    # If the user has an OPENAI_API_KEY or GEMINI_API_KEY passed in via docker run -e, 
    # it will be picked up here.
    try:
        response = agent.run(task)
        output_text = response.content
        
        print("\n--- Task Output ---")
        print(output_text)
        
        # Write to outputs directory
        output_dir = Path("/outputs")
        if output_dir.exists():
            out_file = output_dir / "result.txt"
            with open(out_file, 'w') as f:
                f.write(output_text)
            print(f"\nResult saved to {out_file}")
            
    except Exception as e:
        print(f"\nExecution Error: {e}")
        sys.exit(1)
        
    print("--- Sandbox Execution Completed ---")

if __name__ == "__main__":
    main()
