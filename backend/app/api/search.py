from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.retriever import search_chunks


router = APIRouter(
    prefix="/search",
    tags=["Search"],
)


@router.get("")
def search(
    workspace_id: UUID,
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = q.strip()

    if not query:
        return {
            "workspace_id": str(workspace_id),
            "query": q,
            "results": [],
            "count": 0,
        }

    results = search_chunks(
        db=db,
        query=query,
        workspace_id=workspace_id,
        limit=limit,
    )

    formatted = []

    for result in results:
        formatted.append(
            {
                "chunk_id": str(result.chunk_id),
                "document_id": str(result.document_id),
                "document_title": result.document_title,
                "page_number": result.page_number,
                "text": result.text,
                "vector_similarity": result.vector_similarity,
                "lexical_score": result.lexical_score,
                "rrf_score": result.rrf_score,
                "rerank_score": result.rerank_score,
                "retrieval_sources": result.retrieval_sources,
            }
        )

    return {
        "workspace_id": str(workspace_id),
        "query": query,
        "results": formatted,
        "count": len(formatted),
    }