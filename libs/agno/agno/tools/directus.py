import json
import os
from typing import Any, Dict, List, Optional

from agno.tools import Toolkit
from agno.utils.log import log_debug, log_error

try:
    import httpx
except ImportError:
    raise ImportError("`httpx` not installed. Please install using `pip install httpx`.")


class DirectusTools(Toolkit):
    """
    A toolkit for interacting with a Directus Experiment Ledger.

    This toolkit provides specialized methods for managing experiments, workflows, and tasks
    in a Directus instance.

    Args:
        url (str): The base URL of the Directus instance. Defaults to "http://localhost:8055".
        api_token (Optional[str]): The static API token for authentication.
    """

    def __init__(
        self,
        url: str = "http://localhost:8055",
        api_token: Optional[str] = None,
        **kwargs,
    ):
        self.url = url.rstrip("/")
        self.api_token = api_token or os.getenv("DIRECTUS_API_TOKEN")

        tools: List[Any] = [
            self.list_experiments,
            self.get_experiment,
            self.create_experiment,
            self.update_experiment,
            self.delete_experiment,
            self.list_workflows,
            self.get_workflow,
            self.create_workflow,
            self.update_workflow,
            self.delete_workflow,
            self.list_tasks,
            self.get_task,
            self.create_task,
            self.update_task,
            self.delete_task,
        ]

        super().__init__(name="directus", tools=tools, **kwargs)

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for the API request."""
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Make an HTTP request to the Directus API."""
        url = f"{self.url}/items/{endpoint.lstrip('/')}"
        log_debug(f"Making {method} request to {url}")
        try:
            with httpx.Client() as client:
                response = client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=self._get_headers(),
                    timeout=30.0,
                )
                response.raise_for_status()

                # Directus returns data in a "data" key
                response_json = response.json()
                if response.status_code == 204:
                    return "Success"
                return json.dumps(response_json.get("data", {}), indent=2)
        except httpx.HTTPStatusError as e:
            log_error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"})
        except Exception as e:
            log_error(f"Error making request: {str(e)}")
            return json.dumps({"error": str(e)})

    # --- Experiments ---

    def list_experiments(self, params: Optional[Dict[str, Any]] = None) -> str:
        """List all experiments.

        Args:
            params (Optional[Dict[str, Any]]): Optional query parameters for filtering, sorting, etc.
                Example: {"filter": {"track": {"_eq": "lab"}}}
        """
        return self._make_request("GET", "experiments", params=params)

    def get_experiment(self, experiment_id: str) -> str:
        """Get a specific experiment by ID."""
        return self._make_request("GET", f"experiments/{experiment_id}")

    def create_experiment(
        self,
        hypothesis: str,
        impact: int,
        confidence: int,
        ease: int,
        goal_id: Optional[str] = None,
        track: str = "lab",
        learning_log: Optional[str] = None,
    ) -> str:
        """Create a new experiment.

        Args:
            hypothesis (str): The hypothesis to test.
            impact (int): Impact score (1-10).
            confidence (int): Confidence score (1-10).
            ease (int): Ease score (1-10).
            goal_id (Optional[str]): ID of the parent goal.
            track (str): Track type ('lab', 'engine', 'dead'). Defaults to 'lab'.
            learning_log (Optional[str]): Markdown content for "Validated Learning".
        """
        data = {
            "hypothesis": hypothesis,
            "impact": impact,
            "confidence": confidence,
            "ease": ease,
            "goal_id": goal_id,
            "track": track,
            "learning_log": learning_log,
        }
        return self._make_request("POST", "experiments", json_data=data)

    def update_experiment(self, experiment_id: str, **kwargs) -> str:
        """Update an existing experiment.

        Args:
            experiment_id (str): The ID of the experiment to update.
            **kwargs: Fields to update (hypothesis, impact, confidence, ease, track, etc.)
        """
        return self._make_request("PATCH", f"experiments/{experiment_id}", json_data=kwargs)

    def delete_experiment(self, experiment_id: str) -> str:
        """Delete an experiment."""
        return self._make_request("DELETE", f"experiments/{experiment_id}")

    # --- Workflows ---

    def list_workflows(self, params: Optional[Dict[str, Any]] = None) -> str:
        """List all workflows."""
        return self._make_request("GET", "workflows", params=params)

    def get_workflow(self, workflow_id: str) -> str:
        """Get a specific workflow by ID."""
        return self._make_request("GET", f"workflows/{workflow_id}")

    def create_workflow(
        self,
        name: str,
        experiment_id: Optional[str] = None,
        status: str = "draft",
        process_steps: Optional[Dict[str, Any]] = None,
        efficiency_metric: Optional[float] = None,
        retention_metric: Optional[float] = None,
    ) -> str:
        """Create a new workflow.

        Args:
            name (str): Name of the workflow.
            experiment_id (Optional[str]): Originating experiment ID.
            status (str): Workflow status ('draft', 'validated'). Defaults to 'draft'.
            process_steps (Optional[Dict[str, Any]]): Structured sequence of steps (JSONB).
            efficiency_metric (Optional[float]): Tracking "Engine" health.
            retention_metric (Optional[float]): Tracking "Engine" health.
        """
        data = {
            "name": name,
            "experiment_id": experiment_id,
            "status": status,
            "process_steps": process_steps,
            "efficiency_metric": efficiency_metric,
            "retention_metric": retention_metric,
        }
        return self._make_request("POST", "workflows", json_data=data)

    def update_workflow(self, workflow_id: str, **kwargs) -> str:
        """Update an existing workflow."""
        return self._make_request("PATCH", f"workflows/{workflow_id}", json_data=kwargs)

    def delete_workflow(self, workflow_id: str) -> str:
        """Delete a workflow."""
        return self._make_request("DELETE", f"workflows/{workflow_id}")

    # --- Tasks ---

    def list_tasks(self, params: Optional[Dict[str, Any]] = None) -> str:
        """List all tasks."""
        return self._make_request("GET", "tasks", params=params)

    def get_task(self, task_id: str) -> str:
        """Get a specific task by ID."""
        return self._make_request("GET", f"tasks/{task_id}")

    def create_task(
        self,
        description: str,
        experiment_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        priority: int = 1,
        is_completed: bool = False,
        deadline_gravity: Optional[str] = None,
    ) -> str:
        """Create a new task.

        Note: Task must belong to either an experiment or a workflow.

        Args:
            description (str): Description of the task.
            experiment_id (Optional[str]): ID of the related experiment.
            workflow_id (Optional[str]): ID of the related workflow.
            priority (int): Task priority. Defaults to 1.
            is_completed (bool): Completion status. Defaults to False.
            deadline_gravity (Optional[str]): Deadline for legal/external obligations (ISO format).
        """
        data = {
            "description": description,
            "experiment_id": experiment_id,
            "workflow_id": workflow_id,
            "priority": priority,
            "is_completed": is_completed,
            "deadline_gravity": deadline_gravity,
        }
        return self._make_request("POST", "tasks", json_data=data)

    def update_task(self, task_id: str, **kwargs) -> str:
        """Update an existing task."""
        return self._make_request("PATCH", f"tasks/{task_id}", json_data=kwargs)

    def delete_task(self, task_id: str) -> str:
        """Delete a task."""
        return self._make_request("DELETE", f"tasks/{task_id}")
