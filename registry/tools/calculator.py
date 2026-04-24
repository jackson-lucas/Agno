from agno.tools.toolkit import Toolkit

class CalculatorTools(Toolkit):
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        return a - b

calculator_toolkit = CalculatorTools()
