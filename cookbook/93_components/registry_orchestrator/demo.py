import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Ensure we can import from agno if this is run locally
repo_root = Path(__file__).parent.parent.parent.parent.resolve()
sys.path.append(str(repo_root / "libs" / "agno"))

from agno.knowledge.embedder.google import GeminiEmbedder
from agno.models.google import Gemini
from agno.orchestrator.orchestrator import Orchestrator
from agno.registry.indexer import ComponentIndexer
from agno.registry.loader import RegistryLoader
from agno.vectordb.chroma import ChromaDb


def main():
    load_dotenv()
    if not os.environ.get("GOOGLE_API_KEY") and not os.environ.get("GEMINI_API_KEY"):
        print("Please set the GOOGLE_API_KEY environment variable to run this demo.")
        print("Example: export GOOGLE_API_KEY='AIza...'")
        return

    # 1. Load Registry
    registry_path = repo_root / "registry"
    print(f"Loading registry from {registry_path}...")
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()

    # 2. Setup Vector DB and Indexer
    # Use the Gemini embedder
    chroma_path = repo_root / "tmp" / "chromadb_real_gemini"
    vector_db = ChromaDb(
        collection="agno_registry_gemini",
        path=str(chroma_path),
        persistent_client=True,
        embedder=GeminiEmbedder(),
    )
    registry.vector_db = vector_db

    print("Indexing components into ChromaDB (this may take a moment)...")
    indexer = ComponentIndexer(vector_db)
    indexer.index_registry(registry)

    # 3. Initialize Orchestrator
    orchestrator = Orchestrator(registry, model=Gemini(id="gemini-2.5-flash"))
    print("\nOrchestrator initialized and ready.")

    print("\n--- Agno Semantic Orchestrator ---")
    print("Type a prompt to generate a Job Manifest. Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nPrompt: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input.strip():
                continue

            print("Analyzing request and searching registry...")
            manifest = orchestrator.plan(user_input)
            print("\n--- Job Manifest ---")
            print(manifest.model_dump_json(indent=2))
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error during orchestration: {e}")


if __name__ == "__main__":
    main()
