from typing import Any

from sqlalchemy.orm import Session

from app.services.agent.executor import AgentExecutor
from app.services.agent.reasoning import AgentReasoner
from app.services.agent.schemas import (
    AgentStep,
    AgentTraceEvent,
    ToolResult,
)


class AgentLoop:

    MAX_STEPS = 6

    def __init__(
        self,
        reasoner: AgentReasoner | None = None,
        executor: AgentExecutor | None = None,
    ) -> None:

        self.reasoner = reasoner or AgentReasoner()
        self.executor = executor or AgentExecutor()

    @staticmethod
    def _normalize_arguments(
        tool: str,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        if not isinstance(arguments, dict):
            arguments = {}

        if tool == "search":

            query = str(
                arguments.get("query")
                or arguments.get("entity")
                or ""
            ).strip()

            try:
                limit = int(
                    arguments.get(
                        "limit",
                        5,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                limit = 5

            return {
                "query": query,
                "limit": max(
                    1,
                    min(limit, 10),
                ),
            }

        if tool == "knowledge":

            query = str(
                arguments.get("query")
                or arguments.get("entity")
                or ""
            ).strip()

            return {
                "query": query,
            }

        if tool == "timeline":

            query = str(
                arguments.get("query")
                or arguments.get("entity")
                or ""
            ).strip()

            return {
                "query": query,
            }

        if tool == "calculator":

            expression = str(
                arguments.get(
                    "expression",
                    "",
                )
            ).strip()

            return {
                "expression": expression,
            }

        return arguments

    @staticmethod
    def _signature(
        tool: str,
        arguments: dict[str, Any],
    ) -> str:

        return (
            f"{tool}:"
            + "|".join(
                f"{key}={arguments[key]}"
                for key in sorted(arguments)
            )
        )

    def run(
        self,
        db: Session,
        workspace_id,
        question: str,
    ) -> tuple[
        list[AgentStep],
        list[AgentTraceEvent],
        list[ToolResult],
    ]:

        steps: list[AgentStep] = []
        trace: list[AgentTraceEvent] = []
        tool_results: list[ToolResult] = []

        seen_signatures: set[str] = set()

        for step_number in range(
            1,
            self.MAX_STEPS + 1,
        ):

            decision = self.reasoner.decide(
                question=question,
                steps=steps,
                tool_results=tool_results,
            )

            action = decision["action"]
            tool = decision["tool"]
            reason = decision["reason"]
            arguments = self._normalize_arguments(
                tool=tool,
                arguments=decision["arguments"],
            )

            if action == "finish":

                trace.append(
                    AgentTraceEvent(
                        step_number=step_number,
                        action="finish",
                        tool=None,
                        reason=reason
                        or "Sufficient evidence collected.",
                        outcome=(
                            "Agent decided that enough evidence "
                            "was available for synthesis."
                        ),
                    )
                )

                break

            signature = self._signature(
                tool,
                arguments,
            )

            if signature in seen_signatures:

                trace.append(
                    AgentTraceEvent(
                        step_number=step_number,
                        action="tool",
                        tool=tool,
                        reason=reason,
                        outcome=(
                            "Duplicate tool call prevented."
                        ),
                    )
                )

                # Give the reasoner another opportunity with the
                # duplicate action visible in previous_actions.
                steps.append(
                    AgentStep(
                        tool=tool,
                        reason=(
                            reason
                            + " "
                            + "This action was already attempted."
                        ).strip(),
                        arguments=arguments,
                    )
                )

                continue

            seen_signatures.add(signature)

            step = AgentStep(
                tool=tool,
                reason=reason,
                arguments=arguments,
            )

            steps.append(step)

            results = self.executor.execute(
                db=db,
                workspace_id=workspace_id,
                steps=[step],
            )

            result = results[0]

            tool_results.append(result)

            if result.success:

                outcome = (
                    f"{tool} executed successfully."
                )

            else:

                outcome = (
                    f"{tool} failed: "
                    f"{result.error}"
                )

            trace.append(
                AgentTraceEvent(
                    step_number=step_number,
                    action="tool",
                    tool=tool,
                    reason=reason,
                    outcome=outcome,
                )
            )

        else:

            trace.append(
                AgentTraceEvent(
                    step_number=self.MAX_STEPS,
                    action="finish",
                    tool=None,
                    reason="Maximum research steps reached.",
                    outcome=(
                        "Research loop stopped safely after "
                        f"{self.MAX_STEPS} steps."
                    ),
                )
            )

        return (
            steps,
            trace,
            tool_results,
        )