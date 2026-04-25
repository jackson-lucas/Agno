# Agno Fork: Agentic Git & Sandbox Capabilities

This fork extends the core [Agno](https://github.com/agno-agi/agno) framework with advanced agentic git workflows and enhanced sandbox capabilities.

## Key Differences

### 1. Unified Registry Structure
We have unified the project structure to bundle registry components and skills directly within the `agno` package.
- **Before**: Components were split between root `registry/` and `libs/agno/agno/`.
- **After**: All components reside in `libs/agno/agno/registry/` and `libs/agno/agno/skills/`.
- **Benefit**: Easier distribution, simplified sandbox mounting, and better package integrity.

### 2. Agentic Git Workflow (`CodingWorkflow`)
A specialized multi-agent pipeline for automated code implementation and validation.
- **Planner**: Creates technical implementation plans.
- **Coder**: Implements the logic using specialized file and shell tools.
- **Validator**: Runs guardrails (lints/tests) with a one-time self-fix loop.
- **CommitManager**: Handles conventional commits and PR creation.

### 3. Enhanced Sandbox Ingestion
The Agno sandbox now supports automatic repository ingestion:
- **Remote Ingestion**: Clones a Git repository directly into the sandbox.
- **Local Ingestion**: Mounts a local directory into the sandbox for development.
- **Credential Injection**: Automatically injects `.env` secrets (e.g., `GITHUB_TOKEN`, `OPENAI_API_KEY`) into the sandbox environment.

## How to Use

### Running the Coding Workflow
The `CodingWorkflow` can be triggered via the `JobManifest`.

```python
from agno.orchestrator import JobManifest
from agno.sandbox import DockerRunner

manifest = JobManifest(
    task="Implement a new login endpoint",
    repo_url="https://github.com/user/repo.git",
    test_commands=["pytest"],
    lint_commands=["ruff check"]
)

runner = DockerRunner()
runner.run_job(manifest)
```

### Custom Toolkits
We provide specialized toolkits for Git operations:
- `GitToolkit`: Local git operations (status, add, commit, branch).
- `GitHubToolkit`: High-level GitHub operations (PR creation) using the `gh` CLI.

## Development Setup

1. **Local Setup**: Run `./scripts/dev_setup.sh` to initialize the environment.
2. **Sandbox Setup**: The sandbox uses `Dockerfile.sandbox` which is pre-configured with Git, GitHub CLI, and the necessary Python dependencies.
3. **Environment**: Ensure your `.env` file contains `GITHUB_TOKEN` for PR operations.

## Contributing
Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for all contributions.
- `feat`: New features
- `fix`: Bug fixes
- `refactor`: Structural changes (like the registry unification)
