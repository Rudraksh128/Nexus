from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.assumption import Assumption
from app.models.claim import Claim
from app.models.decision import Decision
from app.models.decision_dependency import DecisionDependency
from app.models.decision_impact import DecisionImpact


class DecisionRepository:

    def create_decision(
        self,
        db: Session,
        workspace_id: UUID,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        confidence: float | None = None,
    ) -> Decision:

        decision = Decision(
            workspace_id=workspace_id,
            title=title,
            description=description,
            priority=priority,
            confidence=confidence,
        )

        db.add(decision)
        db.flush()

        return decision

    def create_assumption(
        self,
        db: Session,
        workspace_id: UUID,
        name: str,
        description: str | None = None,
        confidence: float | None = None,
    ) -> Assumption:

        assumption = Assumption(
            workspace_id=workspace_id,
            name=name,
            description=description,
            confidence=confidence,
        )

        db.add(assumption)
        db.flush()

        return assumption

    def create_dependency(
        self,
        db: Session,
        decision_id: UUID,
        dependency_type: str,
        assumption_id: UUID | None = None,
        claim_id: UUID | None = None,
        confidence: float | None = None,
    ) -> DecisionDependency:

        dependency = DecisionDependency(
            decision_id=decision_id,
            dependency_type=dependency_type,
            assumption_id=assumption_id,
            claim_id=claim_id,
            confidence=confidence,
        )

        db.add(dependency)
        db.flush()

        return dependency

    def get_decision(
        self,
        db: Session,
        decision_id: UUID,
    ) -> Decision | None:

        return db.get(
            Decision,
            decision_id,
        )

    def get_dependencies(
        self,
        db: Session,
        decision_id: UUID,
    ) -> list[DecisionDependency]:

        statement = (
            select(DecisionDependency)
            .where(
                DecisionDependency.decision_id
                == decision_id
            )
        )

        return (
            db.execute(statement)
            .scalars()
            .all()
        )

    def create_impact(
        self,
        db: Session,
        decision_id: UUID,
        impact_type: str,
        severity: str,
        explanation: str,
        source_claim_id: UUID | None = None,
        confidence: float | None = None,
    ) -> DecisionImpact:

        impact = DecisionImpact(
            decision_id=decision_id,
            source_claim_id=source_claim_id,
            impact_type=impact_type,
            severity=severity,
            explanation=explanation,
            confidence=confidence,
        )

        db.add(impact)
        db.flush()

        return impact