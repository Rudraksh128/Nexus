from uuid import UUID

from sqlalchemy.orm import Session

from app.services.decisions.analyzer import DecisionAnalyzer
from app.services.decisions.repository import DecisionRepository


class DecisionService:

    def __init__(self) -> None:

        self.repository = DecisionRepository()
        self.analyzer = DecisionAnalyzer()

    def create_decision(
        self,
        db: Session,
        workspace_id: UUID,
        title: str,
        description: str | None = None,
        priority: str = "medium",
        confidence: float | None = None,
    ):

        decision = self.repository.create_decision(
            db=db,
            workspace_id=workspace_id,
            title=title,
            description=description,
            priority=priority,
            confidence=confidence,
        )

        db.commit()
        db.refresh(decision)

        return decision

    def create_assumption(
        self,
        db: Session,
        workspace_id: UUID,
        name: str,
        description: str | None = None,
        confidence: float | None = None,
    ):

        assumption = self.repository.create_assumption(
            db=db,
            workspace_id=workspace_id,
            name=name,
            description=description,
            confidence=confidence,
        )

        db.commit()
        db.refresh(assumption)

        return assumption

    def connect_dependency(
        self,
        db: Session,
        decision_id: UUID,
        dependency_type: str,
        assumption_id: UUID | None = None,
        claim_id: UUID | None = None,
        confidence: float | None = None,
    ):

        decision = self.repository.get_decision(
            db,
            decision_id,
        )

        if decision is None:
            raise ValueError(
                "Decision not found."
            )

        dependency = self.repository.create_dependency(
            db=db,
            decision_id=decision_id,
            dependency_type=dependency_type,
            assumption_id=assumption_id,
            claim_id=claim_id,
            confidence=confidence,
        )

        db.commit()
        db.refresh(dependency)

        return dependency

    def analyze(
        self,
        db: Session,
        decision_id: UUID,
    ):

        return self.analyzer.analyze(
            db=db,
            decision_id=decision_id,
        )