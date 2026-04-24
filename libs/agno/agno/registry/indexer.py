from typing import Optional, Union, Any
from pathlib import Path
from agno.registry.registry import Registry
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.document.base import Document
from agno.agent.agent import Agent
from agno.tools.toolkit import Toolkit
from agno.tools.function import Function
from agno.workflow.workflow import Workflow
from agno.guardrails.base import BaseGuardrail
from agno.utils.log import log_info, log_error

class ComponentIndexer:
    """
    ComponentIndexer creates semantic embeddings for components within a Registry
    and stores them in a Vector Database (ChromaDB) for semantic retrieval.
    """
    def __init__(self, vector_db: ChromaDb):
        self.vector_db = vector_db
        # Ensure collection is created
        self.vector_db.create()

    def index_registry(self, registry: Registry):
        """Iterates over registry components and indexes them into the vector db."""
        log_info(f"Indexing registry '{registry.name}' into ChromaDB...")
        documents = []

        # 1. Tools
        for tool in registry.tools:
            doc = self._create_document_for_tool(tool)
            if doc: documents.append(doc)

        # 2. Agents
        for agent in registry.agents:
            doc = self._create_document_for_agent(agent)
            if doc: documents.append(doc)

        # 3. Workflows
        for workflow in registry.workflows:
            doc = self._create_document_for_workflow(workflow)
            if doc: documents.append(doc)

        # 4. Guardrails
        for guardrail in registry.guardrails:
            doc = self._create_document_for_guardrail(guardrail)
            if doc: documents.append(doc)

        if documents:
            # Upsert into vector DB. 
            self.vector_db.upsert(content_hash="registry_index", documents=documents)
            log_info(f"Indexed {len(documents)} components successfully.")
        else:
            log_info("No components found to index.")

    def _create_document_for_tool(self, tool: Union[Toolkit, Function, Any]) -> Optional[Document]:
        try:
            if isinstance(tool, Toolkit):
                content = f"Toolkit: {tool.name}\n"
                if tool.instructions:
                    content += f"Instructions: {tool.instructions}\n"
                content += "Functions:\n"
                for func_name, func in tool.functions.items():
                    content += f"- {func_name}: {func.description}\n"
                return Document(
                    id=tool.name,
                    name=tool.name,
                    content=content,
                    meta_data={"type": "tool", "name": tool.name}
                )
            elif getattr(tool, "name", None):
                name = tool.name
                content = f"Tool: {name}\n"
                if getattr(tool, "description", None):
                    content += f"Description: {tool.description}\n"
                return Document(
                    id=name,
                    name=name,
                    content=content,
                    meta_data={"type": "tool", "name": name}
                )
        except Exception as e:
            log_error(f"Failed to create document for tool {tool}: {e}")
        return None

    def _create_document_for_agent(self, agent: Agent) -> Optional[Document]:
        try:
            content = f"Agent: {agent.name}\n"
            if agent.description:
                content += f"Description: {agent.description}\n"
            if agent.instructions:
                instructions_str = agent.instructions if isinstance(agent.instructions, str) else " ".join(agent.instructions)
                content += f"Instructions: {instructions_str}\n"
            agent_id = getattr(agent, "id", None) or agent.name
            return Document(
                id=agent_id,
                name=agent.name,
                content=content,
                meta_data={"type": "agent", "name": agent.name, "id": agent_id}
            )
        except Exception as e:
            log_error(f"Failed to create document for agent {agent.name}: {e}")
        return None

    def _create_document_for_workflow(self, workflow: Workflow) -> Optional[Document]:
        try:
            name = getattr(workflow, "name", workflow.__class__.__name__)
            description = getattr(workflow, "description", "")
            content = f"Workflow: {name}\n"
            if description:
                content += f"Description: {description}\n"
            workflow_id = getattr(workflow, "id", None) or name
            return Document(
                id=workflow_id,
                name=name,
                content=content,
                meta_data={"type": "workflow", "name": name, "id": workflow_id}
            )
        except Exception as e:
            log_error(f"Failed to create document for workflow: {e}")
        return None

    def _create_document_for_guardrail(self, guardrail: BaseGuardrail) -> Optional[Document]:
        try:
            name = getattr(guardrail, "name", guardrail.__class__.__name__)
            description = guardrail.__doc__ or ""
            content = f"Guardrail: {name}\n"
            if description:
                content += f"Description: {description}\n"
            return Document(
                id=name,
                name=name,
                content=content,
                meta_data={"type": "guardrail", "name": name}
            )
        except Exception as e:
            log_error(f"Failed to create document for guardrail: {e}")
        return None
