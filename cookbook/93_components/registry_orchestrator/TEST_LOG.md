### demo.py

**Status:** PASS

**Description:** The script successfully loads the components from the `/registry/` directory into the local ChromaDB vector store. Upon receiving user input, it queries the vector store, retrieving the correct items (e.g. `PII Filter` and `Calculator`), and passes them to the Orchestrator. The Orchestrator leverages an OpenAI model to reason about the retrieved tools and outputs a validated `JobManifest`.

**Result:** PASS. The integration between the Pluggable Registry, ChromaDB indexing, and Orchestrator routing functions perfectly.
