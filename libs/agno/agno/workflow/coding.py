from pathlib import Path
from typing import List, Optional, Any
from pydantic import BaseModel, Field
from agno.workflow import Workflow
from agno.agent import Agent
from agno.tools.file import FileTools
from agno.tools.shell import ShellTools
from agno.tools.git_toolkit import GitToolkit
from agno.tools.github_toolkit import GitHubToolkit
from agno.utils.log import log_info, log_error
from agno.orchestrator.orchestrator import JobManifest

class CodingWorkflow(Workflow):
    """
    CodingWorkflow orchestrates the process of analyzing, implementing,
    validating, and submitting code changes within a sandbox.
    """
    def __init__(
        self,
        name: str = "coding_workflow",
        workspace_path: str = "/app/workspace",
        **kwargs
    ):
        super().__init__(name=name, **kwargs)
        self.workspace_path = Path(workspace_path)
        
        # Tools
        self.file_tools = FileTools(base_dir=self.workspace_path)
        self.shell_tools = ShellTools(base_dir=self.workspace_path)
        self.git_tools = GitToolkit(workspace_path=str(self.workspace_path))
        self.github_tools = GitHubToolkit()
        
        # History is shared across agents in the same session by default in Agno
        # if we pass the same session_id or use the workflow's internal state.
        
    def _get_planner_agent(self) -> Agent:
        return Agent(
            name="Planner",
            description="You are a senior technical planner. Analyze the codebase and the task to create a detailed implementation plan.",
            instructions=[
                "1. Explore the codebase using file tools.",
                "2. Identify the files that need modification.",
                "3. Outline the specific changes required.",
                "4. Output a technical implementation plan."
            ],
            tools=[self.file_tools],
            model=self.agent.model if self.agent else None
        )

    def _get_coder_agent(self) -> Agent:
        return Agent(
            name="Coder",
            description="You are an expert software engineer. Implement the changes requested in the plan.",
            instructions=[
                "1. Follow the implementation plan provided by the Planner.",
                "2. Adhere to project coding standards and best practices.",
                "3. Use file tools to apply changes.",
                "4. If you encounter issues, explain them clearly."
            ],
            tools=[self.file_tools, self.shell_tools],
            model=self.agent.model if self.agent else None
        )

    def _get_validator_agent(self) -> Agent:
        return Agent(
            name="Validator",
            description="You are a QA engineer. Validate that the code changes meet the requirements and don't introduce regressions.",
            instructions=[
                "1. Review the changes made by the Coder.",
                "2. Check for logic errors or missing edge cases.",
                "3. If something is wrong, provide specific feedback for the Coder to fix it."
            ],
            tools=[self.file_tools, self.shell_tools],
            model=self.agent.model if self.agent else None
        )

    def _get_commit_agent(self) -> Agent:
        return Agent(
            name="CommitManager",
            description="You are a repository manager. Finalize the work by committing and submitting a PR.",
            instructions=[
                "1. Generate a standardized commit message based on the work history.",
                "2. Commit the changes.",
                "3. Push the changes and create a Pull Request.",
                "4. Use a clear and descriptive PR title and body."
            ],
            tools=[self.git_tools, self.github_tools],
            model=self.agent.model if self.agent else None
        )

    def run(self, manifest: JobManifest) -> str:
        log_info(f"Starting CodingWorkflow for task: {manifest.task}")
        
        # 1. Plan
        planner = self._get_planner_agent()
        plan_response = planner.run(f"Create a plan for this task: {manifest.task}")
        plan = plan_response.content
        log_info("Implementation plan created.")
        
        # 2. Implement & Validate Loop
        coder = self._get_coder_agent()
        validator = self._get_validator_agent()
        
        implementation_attempt = 1
        max_attempts = 2 # Initial + 1 self-fix
        
        current_task_input = f"Implement the following plan:\n{plan}\n\nContext: {manifest.task}"
        
        while implementation_attempt <= max_attempts:
            log_info(f"Implementation attempt {implementation_attempt}...")
            coder_response = coder.run(current_task_input)
            
            # 3. Validate
            validation_passed = True
            validation_feedback = ""
            
            # 3a. Automated Guardrails (Tests/Lints)
            if manifest.test_commands or manifest.lint_commands:
                log_info("Running automated guardrails...")
                for cmd in manifest.lint_commands + manifest.test_commands:
                    result = self.shell_tools.run_shell_command(cmd.split())
                    if "Error:" in result or "FAILED" in result.upper():
                        validation_passed = False
                        validation_feedback += f"Command '{cmd}' failed:\n{result}\n"
            
            # 3b. Agent Validation (Fallback or Supplemental)
            if validation_passed:
                log_info("Running Agent validation...")
                val_response = validator.run(f"Validate the changes for task: {manifest.task}\nCoder response: {coder_response.content}")
                if "FAIL" in val_response.content.upper() or "FIX" in val_response.content.upper():
                    validation_passed = False
                    validation_feedback += val_response.content
            
            if validation_passed:
                log_info("Validation passed!")
                break
            else:
                log_info(f"Validation failed. Feedback: {validation_feedback}")
                if implementation_attempt < max_attempts:
                    current_task_input = f"Your previous implementation failed validation. Please fix the following issues and try again:\n{validation_feedback}"
                    implementation_attempt += 1
                else:
                    log_error("Max self-fix attempts reached. Workflow failed validation.")
                    return f"Failed validation after {max_attempts} attempts. Last feedback: {validation_feedback}"

        # 4. Submit
        log_info("Submitting changes...")
        committer = self._get_commit_agent()
        submit_response = committer.run(f"Commit and submit PR for the work done. Task: {manifest.task}")
        
        return f"Workflow completed successfully.\n{submit_response.content}"
