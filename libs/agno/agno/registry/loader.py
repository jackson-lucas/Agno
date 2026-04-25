import importlib.util
import inspect
from pathlib import Path
from typing import Any, List, Optional, Type, Union

from agno.agent.agent import Agent
from agno.guardrails.base import BaseGuardrail
from agno.registry.registry import Registry
from agno.team.team import Team
from agno.tools.toolkit import Toolkit
from agno.tools.function import Function
from agno.workflow.workflow import Workflow
from agno.utils.log import log_debug, log_error


class RegistryLoader:
    """
    RegistryLoader scans a directory for Agno components and populates a Registry.
    """

    def __init__(self, root_path: Optional[Union[str, Path]] = None):
        if root_path is None:
            # Default to the directory where this file is located
            self.root_path = Path(__file__).parent.resolve()
        else:
            self.root_path = Path(root_path).resolve()

    def load_all(self) -> Registry:
        """
        Scan all subdirectories and return a populated Registry.
        """
        registry = Registry(name="Local Registry", description=f"Loaded from {self.root_path}")

        # Load tools
        registry.tools.extend(self.load_components(self.root_path / "tools", (Toolkit, Function)))
        
        # Load agents
        registry.agents.extend(self.load_components(self.root_path / "agents", Agent))
        
        # Load workflows
        registry.workflows.extend(self.load_components(self.root_path / "workflows", Workflow))
        
        # Load guardrails
        registry.guardrails.extend(self.load_components(self.root_path / "guardrails", BaseGuardrail))

        return registry

    def load_components(self, directory: Path, component_types: Union[Type, tuple]) -> List[Any]:
        """
        Scan a directory for components of a specific type.
        """
        components = []
        if not directory.exists() or not directory.is_dir():
            log_debug(f"Directory {directory} does not exist, skipping.")
            return components

        for file_path in directory.rglob("*.py"):
            if file_path.name == "__init__.py":
                continue

            try:
                module = self._import_module(file_path)
                if module:
                    # Find all instances of component_types in the module
                    for name, obj in inspect.getmembers(module):
                        if isinstance(obj, component_types):
                            # For classes, we might want to ensure they are not just the class definition
                            # but actual instances. inspect.getmembers with isinstance handles this.
                            components.append(obj)
                            log_debug(f"Loaded {type(obj).__name__} '{name}' from {file_path}")
            except Exception as e:
                log_error(f"Failed to load components from {file_path}: {e}")

        return components

    def _import_module(self, file_path: Path) -> Optional[Any]:
        """
        Dynamically import a Python module from a file path.
        """
        module_name = file_path.stem
        spec = importlib.util.spec_from_file_location(module_name, str(file_path))
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        return None
