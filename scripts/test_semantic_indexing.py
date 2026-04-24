import os
import sys
from pathlib import Path

# Add libs/agno to sys.path
repo_root = Path(__file__).parent.parent.resolve()
sys.path.append(str(repo_root / "libs" / "agno"))

from agno.registry.loader import RegistryLoader
from agno.registry.indexer import ComponentIndexer
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.base import Embedder
from agno.utils.log import set_log_level_to_debug

class MockEmbedder(Embedder):
    def get_embedding(self, text: str):
        # Return a fake 384-dimensional embedding
        return [0.1] * 384
        
    def get_embedding_and_usage(self, text: str):
        return self.get_embedding(text), {"prompt_tokens": 10, "total_tokens": 10}

def test_semantic_indexing():
    set_log_level_to_debug()
    
    # 1. Load the registry
    registry_path = repo_root / "registry"
    loader = RegistryLoader(registry_path)
    registry = loader.load_all()
    
    # 2. Setup VectorDB
    chroma_path = repo_root / "tmp" / "chromadb_test"
    vector_db = ChromaDb(
        collection="agno_registry_test",
        path=str(chroma_path),
        persistent_client=True,
        embedder=MockEmbedder(),
    )
    registry.vector_db = vector_db
    
    # 3. Index components
    indexer = ComponentIndexer(vector_db)
    indexer.index_registry(registry)
    
    # 4. Perform searches
    print("\n--- Semantic Search Tests ---")
    
    # Test 1: Math
    print("\nQuery: 'I need to do some math'")
    results = vector_db.search("I need to do some math", limit=10)
    found_toolkit = False
    for doc in results:
        print(f"Result: {doc.name} (Type: {doc.meta_data.get('type')})")
        if doc.name == "toolkit" or doc.meta_data.get('name') == "toolkit":
            found_toolkit = True
    assert found_toolkit

    # Test 2: Security/PII
    print("\nQuery: 'Filter personal information and PII'")
    results = vector_db.search("Filter personal information and PII", limit=10)
    found_pii = False
    for doc in results:
        print(f"Result: {doc.name} (Type: {doc.meta_data.get('type')})")
        if doc.name == "PII Filter" or doc.meta_data.get('name') == "PII Filter":
            found_pii = True
    assert found_pii

if __name__ == "__main__":
    test_semantic_indexing()
