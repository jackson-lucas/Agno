from typing import Optional
from agno.tools.toolkit import Toolkit
from agno.utils.log import log_info, log_error
import os
import subprocess

class GitHubToolkit(Toolkit):
    """
    GitHubToolkit provides tools for interacting with GitHub.
    Uses the 'gh' CLI which must be authenticated via GITHUB_TOKEN.
    """
    def __init__(self):
        super().__init__(name="github_toolkit")
        self.register(self.create_pull_request)

    def create_pull_request(self, title: str, body: str, base: str = "main", head: Optional[str] = None) -> str:
        """
        Create a Pull Request on GitHub.
        Args:
            title: The title of the PR.
            body: The description of the PR.
            base: The branch you want to merge into (default: main).
            head: The branch containing your changes.
        """
        cmd = ["gh", "pr", "create", "--title", title, "--body", body, "--base", base]
        if head:
            cmd.extend(["--head", head])
            
        try:
            # gh pr create requires GITHUB_TOKEN in env
            result = subprocess.run(
                cmd,
                cwd="/app/workspace",
                check=True,
                capture_output=True,
                text=True
            )
            return f"PR Created successfully: {result.stdout.strip()}"
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to create PR: {e.stderr}")
            return f"Error: {e.stderr}"
