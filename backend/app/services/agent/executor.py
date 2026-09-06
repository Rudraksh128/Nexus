from sqlalchemy.orm import Session

from app.services.agent.schemas import AgentStep, ToolResult
from app.services.agent.tools import create_tool_registry


class AgentExecutor:
    def __init__(self) -> None:
        self.tools = create_tool_registry()

    def execute(
        self,
        db: Session,
        workspace_id,
        steps: list[AgentStep],
    ) -> list[ToolResult]:

        results: list[ToolResult] = []

        for step in steps:
            tool = self.tools.get(step.tool)

            if tool is None:
                results.append(
                    ToolResult(
                        tool=step.tool,
                        success=False,
                        error=f"Unknown tool: {step.tool}",
                    )
                )
                continue

            try:
                result = tool.run(
                    db=db,
                    workspace_id=workspace_id,
                    arguments=step.arguments,
                )

                results.append(
                    ToolResult(
                        tool=step.tool,
                        success=bool(result.get("success", False)),
                        data=result,
                        error=result.get("error"),
                    )
                )

            except Exception as exc:
                results.append(
                    ToolResult(
                        tool=step.tool,
                        success=False,
                        error=str(exc),
                    )
                )

        return results