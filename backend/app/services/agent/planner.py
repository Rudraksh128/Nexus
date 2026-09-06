from app.services.agent.schemas import AgentStep
from app.services.knowledge.providers.base import BaseLLMProvider
from app.services.knowledge.providers.ollama_provider import OllamaProvider


PLANNER_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "tool": {
                        "type": "string",
                        "enum": [
                            "search",
                            "knowledge",
                            "timeline",
                            "calculator",
                        ],
                    },
                    "reason": {
                        "type": "string",
                    },
                    "arguments": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                            },
                            "entity": {
                                "type": "string",
                            },
                            "expression": {
                                "type": "string",
                            },
                            "limit": {
                                "type": "integer",
                            },
                        },
                        "additionalProperties": True,
                    },
                },
                "required": [
                    "tool",
                    "reason",
                    "arguments",
                ],
                "additionalProperties": False,
            },
        }
    },
    "required": ["steps"],
    "additionalProperties": False,
}


SYSTEM_PROMPT = """
You are the planning engine of NEXUS.

Your task is to create a research plan for the user's question.

Available tools:

search
- Search source documents.
- arguments:
  query: string
  limit: integer

knowledge
- Inspect structured entities and claims.
- arguments:
  query: string OR entity: string

timeline
- Retrieve historical claims and events.
- arguments:
  query: string

calculator
- Perform mathematical calculations.
- arguments:
  expression: string

Rules:

1. Use only necessary tools.
2. Search is preferred for direct source evidence.
3. Knowledge is preferred for structured entities and claims.
4. Timeline is preferred for historical questions and changes over time.
5. Calculator is preferred for arithmetic.
6. Every tool must receive the correct argument.
7. Never invent tool names.
8. Never answer the question yourself.
9. Use between 1 and 4 steps.
10. Keep queries specific to the user's question.
"""


class AgentPlanner:

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.provider = provider or OllamaProvider()

    def plan(self, question: str) -> list[AgentStep]:

        raw = self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=question,
            output_schema=PLANNER_SCHEMA,
        )

        steps: list[AgentStep] = []

        for item in raw.get("steps", []):

            arguments = item.get("arguments", {})

            if not isinstance(arguments, dict):
                arguments = {}

            steps.append(
                AgentStep(
                    tool=item["tool"],
                    reason=item["reason"],
                    arguments=arguments,
                )
            )

        return steps