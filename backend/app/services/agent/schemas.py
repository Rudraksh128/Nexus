from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentStep:
    tool: str
    reason: str
    arguments: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolResult:
    tool: str
    success: bool
    data: Any = None
    error: str | None = None


@dataclass
class AgentTraceEvent:
    step_number: int
    action: str
    tool: str | None
    reason: str
    outcome: str


@dataclass
class ResearchEvidence:
    source_type: str
    document_id: str | None
    document_title: str | None
    page_number: int | None
    text: str
    relevance: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResearchResult:
    question: str
    answer: str
    steps: list[AgentStep] = field(default_factory=list)
    trace: list[AgentTraceEvent] = field(default_factory=list)
    evidence: list[ResearchEvidence] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)
    confidence: float = 0.0