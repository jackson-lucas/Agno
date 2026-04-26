# Registry & Orchestrator Demo

This cookbook demonstrates how the **Semantic Orchestrator** interacts with the **Pluggable Registry**. It loads the local registry components from the `/registry/` directory, embeds their "semantic signatures" using OpenAI, and indexes them in a local ChromaDB collection. 

When you provide a prompt, the Orchestrator acts as a Semantic Router: it uses an internal tool to search the vector database and selects the best combination of Agents, Tools, Workflows, and Guardrails to construct an executable `JobManifest`.

## Prerequisites

Ensure you have your environment set up and the `GEMINI_API_KEY` defined. The `chromadb` package must also be installed in your virtual environment.

```bash
export GEMINI_API_KEY="AIza..."
```

## Running the Demo

Run this demo using the `demo` virtual environment:

```bash
.venvs/demo/bin/python cookbook/93_components/registry_orchestrator/demo.py
```

## Example Prompts

Once the script starts, it will enter an interactive loop. Try these prompts based on the default registry components:

1. **Math Task**: `"I need an agent that can do math."`
2. **Data Privacy Task**: `"Analyze this data but make sure personal information is filtered out."`
3. **Complex Task**: `"I need a researcher to browse the web, calculate some numbers, and ensure no PII is leaked."`
