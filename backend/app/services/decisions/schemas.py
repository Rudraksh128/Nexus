from dataclasses import dataclass, field
from typing import Any


@dataclass
class DecisionCreate:
    title: str
    description: str | None = None
    priority: str = "medium"
    confidence: float | None = None


@dataclass
class AssumptionCreate:
    name: str
    description: str | None = None
    confidence: float | None = None


@dataclass
class DependencyCreate:
    dependency_type: str
    assumption_id: str | None = None
    claim_id: str | None = None
    confidence: float | None = None


@dataclass
class DecisionImpactResult:
    decision_id: str
    decision_title: str
    status: str
    impact_level: str
    impacted_assumptions: list[dict[str, Any]] = field(
        default_factory=list
    )
    impacted_claims: list[dict[str, Any]] = field(
        default_factory=list
    )
    explanation: str = ""