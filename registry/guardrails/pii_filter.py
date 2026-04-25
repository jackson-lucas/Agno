from typing import Union
from agno.guardrails.base import BaseGuardrail
from agno.run.agent import RunInput
from agno.run.team import TeamRunInput

class PIIFilterGuardrail(BaseGuardrail):
    def __init__(self, name: str = "PII Filter"):
        self.name = name

    def check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Simple mock check for PII."""
        # In a real implementation, this would use regex or a model
        pass

    async def async_check(self, run_input: Union[RunInput, TeamRunInput]) -> None:
        """Simple mock check for PII."""
        pass

pii_filter = PIIFilterGuardrail()
