from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.reports.service import ResearchReportService


router = APIRouter(
    prefix="/reports",
    tags=["Reports"],
)


class ReportRequest(BaseModel):

    workspace_id: UUID

    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
    )


@router.post("/research")
def create_research_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
):

    try:
        service = ResearchReportService()

        return service.generate_report(
            db=db,
            workspace_id=request.workspace_id,
            question=request.question,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc