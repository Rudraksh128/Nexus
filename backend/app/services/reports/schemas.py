from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReportFinding:
    title: str
    explanation: str
    confidence: float


@dataclass
class ReportSection:
    title: str
    content: str


@dataclass
class ResearchReport:
    title: str
    question: str
    executive_summary: str
    findings: list[ReportFinding] = field(default_factory=list)
    sections: list[ReportSection] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0