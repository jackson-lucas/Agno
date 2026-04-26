from typing import List, Optional
from pydantic import BaseModel, Field

from agno.agent.agent import Agent
from agno.registry.registry import Registry
from agno.utils.log import log_info

class JobManifest(BaseModel):
    task: str = Field(..., description="The original task or prompt requested by the user")
    workflow_id: Optional[str] = Field(None, description="The ID or name of the workflow to run")
    agent_ids: List[str] = Field(default_factory=list, description="The IDs or names of the agents to use")
    tool_ids: List[str] = Field(default_factory=list, description="The IDs or names of the tools to attach")
    guardrail_ids: List[str] = Field(default_factory=list, description="The IDs or names of the guardrails to apply")
    repo_url: Optional[str] = Field(None, description="The URL of the remote git repository to clone")
    repo_path: Optional[str] = Field(None, description="The local path of the repository to mount or copy")
    test_commands: List[str] = Field(default_factory=list, description="List of commands to run for testing/validation")
    lint_commands: List[str] = Field(default_factory=list, description="List of commands to run for linting/validation")
    reasoning: str = Field(..., description="The reasoning for the selection")

class Orchestrator:
    """
    The Orchestrator agent uses semantic search over the Registry to select
    the appropriate components for a given task, producing a JobManifest.
    """
    def __init__(self, registry: Registry, model=None):
        self.registry = registry

        # Optional: Allow passing a specific model, defaulting to OpenAI GPT-4o if not provided
        kwargs = {}
        if model:
            kwargs["model"] = model

        self.agent = Agent(
            name="Orchestrator",
            description="You are an AI orchestrator. Your job is to select the best components from the registry to fulfill the user's request.",
            instructions=[
                "You have been provided with a list of available components from the registry.",
                "1. Analyze the user's request and the available components.",
                "2. Select the best combination of components to fulfill the request.",
                "3. Output a JobManifest with your selection."
            ],
            output_schema=JobManifest,
            **kwargs
        )
        
    def plan(self, prompt: str) -> JobManifest:
        """
        Generate a JobManifest for the given prompt.
        """
        registry_context = "Available Components:\n"
        if self.registry.vector_db:
            log_info(f"Orchestrator searching registry for: {prompt}")
            results = self.registry.vector_db.search(query=prompt, limit=5)
            if results:
                for doc in results:
                    metadata = doc.meta_data or {}
                    comp_type = metadata.get('type', 'unknown')
                    comp_id = metadata.get('id', 'unknown')
                    registry_context += f"--- {comp_type.upper()} ID: {comp_id} ---\n{doc.content}\n\n"
            else:
                registry_context += "No matching components found.\n"
        else:
            registry_context += "Vector DB not initialized in registry. Cannot perform semantic search.\n"

        full_prompt = f"User Request: {prompt}\n\n{registry_context}"
        response = self.agent.run(full_prompt)
        # response.content will be an instance of JobManifest because of output_schema
        return response.content
