# Product Requirements Document (PRD): Agno Sandbox Orchestrator (V1)

## 1. Executive Summary
The **Agno Sandbox Orchestrator** is a localized system designed to manage, route, and execute AI agent workflows within isolated environments. Building upon a fork of the Agno framework, this system allows users to define a library of "Lego-brick" components (Agents, Skills, Guardrails, and Workflows) that are semantically selected by an Orchestrator and executed inside an ephemeral Docker sandbox for maximum safety and observability.

---

## 2. Objectives & Goals
* **Safety First:** Execute all LLM-generated code and tool calls in an isolated container to protect the host system.
* **Modularity:** Enable a "hot-swappable" registry where new capabilities are added simply by dropping files into folders.
* **Semantic Intelligence:** Use vector search (ChromaDB) to automatically route user requests to the most relevant agent or workflow.
* **Observability:** Provide a step-by-step "trace" of the agent's reasoning, tool usage, and guardrail validations via a Web UI.

---

## 3. User Flow
1.  **Input:** User sends a natural language request via the Web UI.
2.  **Selection:** The **Orchestrator Agent** queries **ChromaDB** to find the matching Workflow/Agent/Guardrails from the Local Registry.
3.  **Preparation:** The system generates a **Job Manifest** (JSON) defining the execution parameters.
4.  **Sandbox Execution:** A **Docker Container** spins up, mounts the required registry files, and executes the Agno workflow.
5.  **Monitoring:** Traces and logs are streamed from the container to the Host DB.
6.  **Output:** The UI displays the final result and a gallery of any generated **Artifacts** (files, charts, data).

---

## 4. Functional Requirements

### 4.1 Local Registry System
The system must support a file-based registry located at `/registry/` with the following sub-directories:
* **`/tools`**: Python functions wrapped as Agno Toolkits.
* **`/agents`**: Agent definitions (instructions, personas, model configs).
* **`/workflows`**: Multi-agent orchestration logic and step sequences.
* **`/guardrails`**: Input/Output validation logic (e.g., PII filtering, code safety).

### 4.2 Semantic Orchestrator (ChromaDB)
* **Indexing:** On startup, the system must scan the Registry and generate embeddings for each component's description.
* **Routing:** Upon receiving a prompt, the Orchestrator must perform a similarity search in ChromaDB to select the appropriate workflow.
* **Guardrail Mapping:** The Orchestrator must dynamically attach relevant Guardrails based on the intent of the request.

### 4.3 Containerized Sandbox
* **Isolation:** Every request must trigger a fresh Docker container.
* **Resource Limits:** Containers must have CPU and Memory caps to prevent runaway processes.
* **Volume Mounting:** The Registry and an `/outputs` folder must be mounted to the container as read-only and read-write respectively.

### 4.4 Observability & Tracing
* **Real-time Logs:** The Web UI must show a live feed of the Agno `AgentOS` traces (Thinking, Tool Calling, Response).
* **Guardrail Feedback:** The UI must explicitly highlight if a guardrail was triggered (e.g., "Output blocked due to PII detection").

### 4.5 Artifact Management
* **Persistence:** Files generated inside the sandbox must be moved to a host-accessible `/artifacts/<request_id>` folder.
* **Preview:** The Web UI must support rendering common file types (Markdown, Images, CSVs).

---

## 5. Technical Architecture

| Component | Technology |
| :--- | :--- |
| **Agent Framework** | Agno (Custom Fork) |
| **Vector DB** | ChromaDB (Local) |
| **Orchestration API** | FastAPI |
| **Sandbox** | Docker Engine (Python SDK) |
| **Primary Database** | PostgreSQL (shared between Host and Container) |
| **Frontend** | Next.js + Tailwind CSS |
| **Observability** | Agno Tracing Protocol |

---

## 6. Success Metrics
1.  **Routing Accuracy:** 100% of requests correctly mapped to the intended registry workflow.
2.  **Isolation Integrity:** Zero successful escapes from the Docker container to the host filesystem.
3.  **Latency:** Total time from user request to container spin-up should be < 3 seconds.
4.  **Reliability:** 100% of generated artifacts are successfully persisted and viewable in the UI.