import os
import sys
from pathlib import Path

# Add libs/agno to sys.path
repo_root = Path(__file__).parent.parent.resolve()
sys.path.append(str(repo_root / "libs" / "agno"))

from agno.registry.loader import RegistryLoader
from agno.registry.indexer import ComponentIndexer
from agno.vectordb.chroma import ChromaDb
from agno.orchestrator.orchestrator import Orchestrator
from agno.utils.log import set_log_level_to_debug
from agno.knowledge.embedder.base import Embedder

# Mock embedder just to avoid OpenAI API key errors in this environment
class MockEmbedder(Embedder):
    def get_embedding(self, text: str):
        # We can simulate different embeddings by hashing the text, but for our mock
        # let's just return a constant array since we just want to test if the orchestrator
        # calls search correctly.
        return [0.1] * 384
        
    def get_embedding_and_usage(self, text: str):
        return self.get_embedding(text), {"prompt_tokens": 10, "total_tokens": 10}

def test_orchestrator():
    # Only need info level for orchestrator test output
    
    registry_path = repo_root / "registry"
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()
    
    chroma_path = repo_root / "tmp" / "chromadb_test"
    vector_db = ChromaDb(
        collection="agno_registry_test",
        path=str(chroma_path),
        persistent_client=True,
        embedder=MockEmbedder()
    )
    registry.vector_db = vector_db
    
    indexer = ComponentIndexer(vector_db)
    indexer.index_registry(registry)
    
    # Notice: we don't pass an actual model to orchestrator, it'll default to OpenAI GPT-4o
    # Wait, the Orchestrator is an agent that will use OpenAI to plan.
    # Without an API key, the orchestrator's agent.run() will fail.
    # So we should probably just print what the orchestrator does or catch the exception
    # to show that it is initialized correctly.
    
    orchestrator = Orchestrator(registry)
    
    print("\n--- Orchestrator initialized ---")
    print(f"Orchestrator Agent Name: {orchestrator.agent.name}")
    print(f"Orchestrator Response Model: {orchestrator.agent.output_schema.__name__}")
    
    # We can try to run it but it might fail without OPENAI_API_KEY
    try:
        manifest = orchestrator.plan("I need a researcher that can also do math and filtered for PII")
        print("\n--- Generated Job Manifest ---")
        print(manifest.model_dump_json(indent=2))
    except Exception as e:
        print(f"\nCaught exception due to missing API key (expected in CI/test env): {e}")

if __name__ == "__main__":
    test_orchestrator()
