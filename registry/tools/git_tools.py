from agno.tools.git_toolkit import GitToolkit
from agno.tools.github_toolkit import GitHubToolkit
from agno.tools.shell import ShellTools

# Instantiate toolkits
git_toolkit = GitToolkit()
github_toolkit = GitHubToolkit()
shell_tools = ShellTools()

# These will be picked up by the RegistryLoader
components = [
    git_toolkit,
    github_toolkit,
    shell_tools
]
