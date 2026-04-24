import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can import from agno if this is run locally
repo_root = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.append(str(repo_root / "libs" / "agno"))

from agno.registry.loader import RegistryLoader
from agno.registry.indexer import ComponentIndexer
from agno.vectordb.chroma import ChromaDb
from agno.orchestrator.orchestrator import Orchestrator
from agno.sandbox.runner import DockerRunner
from agno.models.google import Gemini
from agno.knowledge.embedder.google import GeminiEmbedder

def main():
    load_dotenv()
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("Please set the GOOGLE_API_KEY environment variable to run this demo.")
        return

    # Check for Observability DB
    import socket
    try:
        with socket.create_connection(("localhost", 5532), timeout=1):
            pass
    except (socket.timeout, ConnectionRefusedError):
        print("\nWARNING: Observability Database (PostgreSQL) is not reachable on localhost:5532.")
        print("Please run: ./scripts/run_observability_db.sh")
        print("Execution will continue, but telemetry/logs will not be captured.\n")

    # 1. Load Registry
    registry_path = repo_root / "registry"
    print(f"Loading registry from {registry_path}...")
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()

    # 2. Setup Vector DB and Indexer
    chroma_path = repo_root / "tmp" / "chromadb_real_gemini"
    vector_db = ChromaDb(
        collection="agno_registry_gemini",
        path=str(chroma_path),
        persistent_client=True,
        embedder=GeminiEmbedder(),
    )
    registry.vector_db = vector_db
    
    print("Indexing components into ChromaDB (if not already indexed)...")
    indexer = ComponentIndexer(vector_db)
    indexer.index_registry(registry)

    # 3. Initialize Orchestrator
    orchestrator = Orchestrator(registry, model=Gemini(id="gemini-2.5-flash"))
    
    # 4. Initialize Runner
    runner = DockerRunner(repo_root)

    print("\n--- Agno Sandbox Orchestrator ---")
    print("Type a prompt. The Orchestrator will plan the execution, and the Sandbox will run it.")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        try:
            user_input = input("\nTask: ")
            if user_input.lower() in ['exit', 'quit']:
                break
            if not user_input.strip():
                continue
            
            print("\n[1/3] Orchestrating: Searching registry and planning job...")
            manifest = orchestrator.plan(user_input)
            
            print("\n[2/3] Generated Job Manifest:")
            print(manifest.model_dump_json(indent=2))
            
            print("\n[3/3] Executing in Docker Sandbox...")
            out_dir = runner.run(manifest)
            
            print(f"\nExecution finished. You can check the output folder at {out_dir}")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
        except Exception as e:
            print(f"Error during orchestration/execution: {e}")

if __name__ == "__main__":
    main()
