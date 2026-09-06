from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics.service import AnalyticsService


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/workspace/{workspace_id}")
def workspace_analytics(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):

    service = AnalyticsService()

    return service.workspace_summary(
        db=db,
        workspace_id=workspace_id,
    )