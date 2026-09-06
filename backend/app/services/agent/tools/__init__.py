from app.services.agent.tools.base import AgentTool
from app.services.agent.tools.calculator import CalculatorTool
from app.services.agent.tools.knowledge import KnowledgeTool
from app.services.agent.tools.search import SearchTool
from app.services.agent.tools.timeline import TimelineTool


def create_tool_registry() -> dict[str, AgentTool]:
    tools = [
        SearchTool(),
        KnowledgeTool(),
        TimelineTool(),
        CalculatorTool(),
    ]

    return {
        tool.name: tool
        for tool in tools
    }