import ast
import operator
from typing import Any

from app.services.agent.tools.base import AgentTool


class SafeCalculator:
    OPERATORS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    @classmethod
    def evaluate(cls, node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value

            raise ValueError("Only numeric constants are allowed.")

        if isinstance(node, ast.UnaryOp):
            operation = cls.OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported unary operator.")

            return operation(cls.evaluate(node.operand))

        if isinstance(node, ast.BinOp):
            operation = cls.OPERATORS.get(type(node.op))

            if operation is None:
                raise ValueError("Unsupported operator.")

            left = cls.evaluate(node.left)
            right = cls.evaluate(node.right)

            return operation(left, right)

        raise ValueError("Unsupported expression.")


class CalculatorTool(AgentTool):
    name = "calculator"

    description = (
        "Perform safe mathematical calculations. "
        "Use this for percentages, growth rates, differences, ratios, "
        "or other numeric calculations."
    )

    def run(
        self,
        db,
        workspace_id,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        expression = str(arguments.get("expression", "")).strip()

        if not expression:
            return {
                "success": False,
                "error": "Expression is required.",
            }

        if len(expression) > 200:
            return {
                "success": False,
                "error": "Expression is too long.",
            }

        try:
            tree = ast.parse(expression, mode="eval")

            result = SafeCalculator.evaluate(tree.body)

            return {
                "success": True,
                "expression": expression,
                "result": result,
            }

        except Exception as exc:
            return {
                "success": False,
                "expression": expression,
                "error": str(exc),
            }