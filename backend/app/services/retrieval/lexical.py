# app/services/retrieval/lexical.py

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.page import DocumentPage


def retrieve_lexical(
    db: Session,
    query: str,
    workspace_id: UUID,
    limit: int = 20,
) -> list[dict]:

    query = query.strip()

    if not query:
        return []

    ts_query = func.plainto_tsquery(
        "english",
        query,
    )

    text_vector = func.to_tsvector(
        "english",
        DocumentChunk.text,
    )

    lexical_score = func.ts_rank_cd(
        text_vector,
        ts_query,
    )

    statement = (
        select(
            DocumentChunk.id,
            DocumentChunk.text,
            DocumentPage.page_number,
            Document.id.label("document_id"),
            Document.title,
            lexical_score.label("lexical_score"),
        )
        .join(
            DocumentPage,
            DocumentChunk.page_id == DocumentPage.id,
        )
        .join(
            Document,
            DocumentPage.document_id == Document.id,
        )
        .where(
            Document.workspace_id == workspace_id,
            DocumentChunk.text.is_not(None),
            text_vector.op("@@")(ts_query),
        )
        .order_by(
            lexical_score.desc()
        )
        .limit(limit)
    )

    rows = db.execute(statement).all()

    results = []

    for rank, row in enumerate(rows, start=1):

        results.append(
            {
                "chunk_id": str(row.id),
                "document_id": str(row.document_id),
                "document_title": row.title,
                "page_number": row.page_number,
                "text": row.text,
                "lexical_score": round(
                    float(row.lexical_score),
                    6,
                ),
                "lexical_rank": rank,
                "rank": rank,
            }
        )

    return results