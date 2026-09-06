from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.decisions.service import DecisionService


router = APIRouter(
    prefix="/decisions",
    tags=["Decision Intelligence"],
)


class DecisionCreateRequest(BaseModel):

    workspace_id: UUID

    title: str = Field(
        ...,
        min_length=3,
        max_length=500,
    )

    description: str | None = None

    priority: str = Field(
        default="medium",
        pattern="^(low|medium|high|critical)$",
    )

    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


class AssumptionCreateRequest(BaseModel):

    workspace_id: UUID

    name: str = Field(
        ...,
        min_length=3,
        max_length=500,
    )

    description: str | None = None

    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


class DependencyRequest(BaseModel):

    dependency_type: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    assumption_id: UUID | None = None

    claim_id: UUID | None = None

    confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
    )


@router.post("")
def create_decision(
    request: DecisionCreateRequest,
    db: Session = Depends(get_db),
):

    try:

        service = DecisionService()

        decision = service.create_decision(
            db=db,
            workspace_id=request.workspace_id,
            title=request.title,
            description=request.description,
            priority=request.priority,
            confidence=request.confidence,
        )

        return {
            "id": str(decision.id),
            "workspace_id": str(
                decision.workspace_id
            ),
            "title": decision.title,
            "description": decision.description,
            "status": decision.status,
            "priority": decision.priority,
            "confidence": decision.confidence,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.post("/assumptions")
def create_assumption(
    request: AssumptionCreateRequest,
    db: Session = Depends(get_db),
):

    service = DecisionService()

    assumption = service.create_assumption(
        db=db,
        workspace_id=request.workspace_id,
        name=request.name,
        description=request.description,
        confidence=request.confidence,
    )

    return {
        "id": str(assumption.id),
        "workspace_id": str(
            assumption.workspace_id
        ),
        "name": assumption.name,
        "description": assumption.description,
        "status": assumption.status,
        "confidence": assumption.confidence,
    }


@router.post("/{decision_id}/dependencies")
def create_dependency(
    decision_id: UUID,
    request: DependencyRequest,
    db: Session = Depends(get_db),
):

    try:

        service = DecisionService()

        dependency = service.connect_dependency(
            db=db,
            decision_id=decision_id,
            dependency_type=request.dependency_type,
            assumption_id=request.assumption_id,
            claim_id=request.claim_id,
            confidence=request.confidence,
        )

        return {
            "id": str(dependency.id),
            "decision_id": str(
                dependency.decision_id
            ),
            "assumption_id": (
                str(dependency.assumption_id)
                if dependency.assumption_id
                else None
            ),
            "claim_id": (
                str(dependency.claim_id)
                if dependency.claim_id
                else None
            ),
            "dependency_type": dependency.dependency_type,
            "confidence": dependency.confidence,
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc


@router.get("/{decision_id}/analysis")
def analyze_decision(
    decision_id: UUID,
    db: Session = Depends(get_db),
):

    try:

        service = DecisionService()

        return service.analyze(
            db=db,
            decision_id=decision_id,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc