import json
from typing import Any

from app.services.agent.schemas import AgentStep, ToolResult
from app.services.knowledge.providers.base import BaseLLMProvider
from app.services.knowledge.providers.ollama_provider import OllamaProvider


REASONING_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {
            "type": "string",
            "enum": [
                "tool",
                "finish",
            ],
        },
        "tool": {
            "type": "string",
            "enum": [
                "search",
                "knowledge",
                "timeline",
                "calculator",
                "none",
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
        "action",
        "tool",
        "reason",
        "arguments",
    ],
    "additionalProperties": False,
}


SYSTEM_PROMPT = """
You are the decision-making engine of NEXUS.

Your job is NOT to answer the user's question.

Your job is to decide the NEXT research action.

Available tools:

search
Purpose:
Search source documents using hybrid semantic + lexical retrieval.

Arguments:
{
  "query": "specific search query",
  "limit": 1-10
}

knowledge
Purpose:
Inspect structured entities and claims already extracted into NEXUS.

Arguments:
{
  "query": "specific knowledge query"
}
or
{
  "entity": "entity name"
}

timeline
Purpose:
Inspect historical claims and events.

Arguments:
{
  "query": "specific historical topic"
}

calculator
Purpose:
Perform mathematical calculations.

Arguments:
{
  "expression": "safe mathematical expression"
}

Decision rules:

1. Use the fewest tools necessary.
2. Start with search when direct source evidence is needed.
3. Use knowledge when structured facts or entities are useful.
4. Use timeline when the question involves time, change, history, or comparison.
5. Use calculator only when an actual calculation is needed.
6. After observing a tool result, decide again.
7. If the available evidence is sufficient to answer the question, choose "finish".
8. Do NOT call the same tool with the same arguments repeatedly.
9. Never invent information.
10. Never answer the user directly.
11. If evidence is insufficient, choose another useful tool.
12. Use "none" as the tool when action is "finish".

The goal is not to use many tools.
The goal is to collect enough reliable evidence to answer correctly.
"""


class AgentReasoner:

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.provider = provider or OllamaProvider()

    @staticmethod
    def _summarize_tool_result(
        result: ToolResult,
    ) -> dict[str, Any]:

        if not result.success:
            return {
                "tool": result.tool,
                "success": False,
                "error": result.error,
            }

        data = result.data

        if not isinstance(data, dict):
            return {
                "tool": result.tool,
                "success": True,
                "data": str(data),
            }

        summary: dict[str, Any] = {
            "tool": result.tool,
            "success": True,
        }

        search_results = data.get("results")

        if isinstance(search_results, list):
            summary["results"] = [
                {
                    "document_title": item.get(
                        "document_title"
                    ),
                    "page_number": item.get(
                        "page_number"
                    ),
                    "text": str(
                        item.get("text", "")
                    )[:1000],
                    "rerank_score": item.get(
                        "rerank_score"
                    ),
                }
                for item in search_results[:5]
                if isinstance(item, dict)
            ]

        entities = data.get("entities")

        if isinstance(entities, list):
            summary["entities"] = entities[:10]

        claims = data.get("claims")

        if isinstance(claims, list):
            summary["claims"] = claims[:10]

        events = data.get("events")

        if isinstance(events, list):
            summary["events"] = events[:10]

        if "result" in data:
            summary["calculation"] = {
                "expression": data.get(
                    "expression"
                ),
                "result": data.get("result"),
            }

        summary["count"] = data.get(
            "count",
            data.get("claim_count"),
        )

        return summary

    def decide(
        self,
        question: str,
        steps: list[AgentStep],
        tool_results: list[ToolResult],
    ) -> dict[str, Any]:

        observations = [
            self._summarize_tool_result(result)
            for result in tool_results
        ]

        previous_actions = [
            {
                "tool": step.tool,
                "reason": step.reason,
                "arguments": step.arguments,
            }
            for step in steps
        ]

        payload = {
            "question": question,
            "previous_actions": previous_actions,
            "observations": observations,
            "instruction": (
                "Choose the next action. "
                "Use finish only when the available evidence "
                "is sufficient."
            ),
        }

        raw = self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            ),
            output_schema=REASONING_SCHEMA,
        )

        action = str(
            raw.get("action", "finish")
        ).strip().lower()

        tool = str(
            raw.get("tool", "none")
        ).strip().lower()

        reason = str(
            raw.get("reason", "")
        ).strip()

        arguments = raw.get(
            "arguments",
            {},
        )

        if not isinstance(arguments, dict):
            arguments = {}

        if action not in {
            "tool",
            "finish",
        }:
            action = "finish"

        allowed_tools = {
            "search",
            "knowledge",
            "timeline",
            "calculator",
        }

        if action == "tool" and tool not in allowed_tools:
            action = "finish"
            tool = "none"

        if action == "finish":
            tool = "none"
            arguments = {}

        return {
            "action": action,
            "tool": tool,
            "reason": reason,
            "arguments": arguments,
        }