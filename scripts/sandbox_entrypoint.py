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
from agno.orchestrator.orchestrator import JobManifest
from agno.workflow.coding import CodingWorkflow
from agno.models.google import Gemini

def main():
    if len(sys.argv) < 2:
        print("Usage: python sandbox_entrypoint.py <path_to_manifest.json>")
        sys.exit(1)

    manifest_path = sys.argv[1]
    with open(manifest_path, 'r') as f:
        data = json.load(f)
        manifest = JobManifest(**data)

    print(f"--- Sandbox Execution Started ---")
    print(f"Task: {manifest.task}")
    
    # Load registry
    registry_path = Path("/registry")
    if not registry_path.exists():
        print("Error: /registry not mounted into the container.")
        sys.exit(1)
        
    print("Loading registry components...")
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()
    
    # Configure Observability DB URL
    db_url = "postgresql+psycopg://ai:ai@host.docker.internal:5532/ai"
    
    # Determine Execution Mode
    if manifest.workflow_id == "CodingWorkflow" or "code" in manifest.task.lower():
        print("Initializing CodingWorkflow...")
        workflow = CodingWorkflow(
            workspace_path="/app/workspace"
        )
        
        # Setup Observability for Workflow
        try:
            from agno.db.postgres import PostgresDb
            db = PostgresDb(db_url=db_url)
            workflow.db = db
            # We also need a default agent for the workflow to use for its internal agents
            workflow.agent = Agent(model=Gemini(id="gemini-2.5-flash"))
        except Exception as e:
            print(f"Warning: Observability setup failed: {e}")
            
        print("\nExecuting Coding Workflow...")
        try:
            output_text = workflow.run(manifest)
            print("\n--- Workflow Output ---")
            print(output_text)
        except Exception as e:
            print(f"\nWorkflow Error: {e}")
            sys.exit(1)
    else:
        # Standard Agent Execution
        agent = None
        if manifest.agent_ids:
            agent_name = manifest.agent_ids[0]
            for a in registry.agents:
                if getattr(a, "id", a.name) == agent_name or a.name == agent_name:
                    agent = a
                    break
        
        if not agent:
            print("Using default Agent.")
            agent = Agent(name="DefaultSandboxAgent", model=Gemini(id="gemini-2.5-flash"))
        else:
            print(f"Using Agent: {agent.name}")

        # Attach Tools
        tools_to_add = []
        for t_id in manifest.tool_ids:
            for t in registry.tools:
                if getattr(t, "name", None) == t_id:
                    tools_to_add.append(t)
                    print(f"Attached Tool: {t.name}")
                    break
        
        if tools_to_add:
            if agent.tools is None:
                agent.tools = []
            agent.tools.extend(tools_to_add)

        # Configure Observability
        print("Configuring Observability Bridge...")
        try:
            from agno.db.postgres import PostgresDb
            from agno.tracing import setup_tracing
            db = PostgresDb(db_url=db_url)
            agent.db = db
            setup_tracing(db=db)
            agent.tracing = True
        except Exception as obs_err:
            print(f"Warning: Could not connect to Observability DB: {obs_err}")

        print("\nExecuting Task...")
        try:
            response = agent.run(manifest.task)
            output_text = response.content
            print("\n--- Task Output ---")
            print(output_text)
        except Exception as e:
            print(f"\nExecution Error: {e}")
            sys.exit(1)
            
    # Finalize
    output_dir = Path("/outputs")
    if output_dir.exists():
        out_file = output_dir / "result.txt"
        with open(out_file, 'w') as f:
            f.write(output_text)
        print(f"\nResult saved to {out_file}")
        
    print("--- Sandbox Execution Completed ---")

if __name__ == "__main__":
    main()
