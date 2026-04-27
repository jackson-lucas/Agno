import subprocess
from typing import List, Optional

from agno.tools.toolkit import Toolkit
from agno.utils.log import log_error, log_info


class GitToolkit(Toolkit):
    """
    GitToolkit provides tools for interacting with a git repository.
    All commands are executed within the /app/workspace directory.
    """

    def __init__(self, workspace_path: str = "/app/workspace"):
        super().__init__(name="git_toolkit")
        self.workspace_path = workspace_path
        self.register(self.git_status)
        self.register(self.git_add)
        self.register(self.git_commit)
        self.register(self.git_push)
        self.register(self.git_branch)

    def _run_git(self, args: List[str]) -> str:
        try:
            result = subprocess.run(["git"] + args, cwd=self.workspace_path, check=True, capture_output=True, text=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            log_error(f"Git command failed: {e.stderr}")
            return f"Error: {e.stderr}"

    def git_status(self) -> str:
        """Get the current status of the repository."""
        return self._run_git(["status"])

    def git_add(self, files: List[str]) -> str:
        """Stage files for commit. Use ['.'] to add all changes."""
        return self._run_git(["add"] + files)

    def git_commit(self, message: str) -> str:
        """Commit staged changes with a message."""
        return self._run_git(["commit", "-m", message])

    def git_push(self, remote: str = "origin", branch: Optional[str] = None) -> str:
        """Push changes to the remote repository."""
        args = ["push", remote]
        if branch:
            args.append(branch)
        return self._run_git(args)

    def git_branch(self, name: str, create: bool = False) -> str:
        """Manage branches. If create is True, a new branch is created."""
        if create:
            return self._run_git(["checkout", "-b", name])
        return self._run_git(["checkout", name])
