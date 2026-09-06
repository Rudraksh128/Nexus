# app/services/retrieval/pipeline.py

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.services.retrieval.fusion import reciprocal_rank_fusion
from app.services.retrieval.lexical import retrieve_lexical
from app.services.retrieval.reranker import (
    BaseReranker,
    create_reranker,
)
from app.services.retrieval.schemas import RetrievalCandidate
from app.services.retrieval.vector import retrieve_vector


_reranker: BaseReranker | None = None


def _get_reranker() -> BaseReranker:

    global _reranker

    if _reranker is None:
        _reranker = create_reranker(
            settings.NEXUS_RERANKER
        )

    return _reranker


def retrieve(
    db: Session,
    query: str,
    workspace_id: UUID,
    limit: int = 5,
    candidate_limit: int = 20,
) -> list[RetrievalCandidate]:

    query = query.strip()

    if not query:
        return []

    vector_results = retrieve_vector(
        db=db,
        query=query,
        workspace_id=workspace_id,
        limit=candidate_limit,
    )

    lexical_results = retrieve_lexical(
        db=db,
        query=query,
        workspace_id=workspace_id,
        limit=candidate_limit,
    )

    fused_results = reciprocal_rank_fusion(
        result_lists=[
            vector_results,
            lexical_results,
        ],
        limit=candidate_limit,
    )

    reranker = _get_reranker()

    return reranker.rerank(
        query=query,
        candidates=fused_results,
        limit=limit,
    )