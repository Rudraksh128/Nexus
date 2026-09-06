from uuid import UUID

from sqlalchemy.orm import Session

from app.services.retrieval.pipeline import (
    retrieve,
)


def search_chunks(
    db: Session,
    query: str,
    workspace_id: UUID,
    limit: int = 5,
) -> list:
    """
    Compatibility entry point for document search.

    Actual retrieval logic lives in the modular
    retrieval pipeline.
    """

    return retrieve(
        db=db,
        query=query,
        workspace_id=workspace_id,
        limit=limit,
    )