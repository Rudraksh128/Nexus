# app/services/retrieval/vector.py

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.page import DocumentPage
from app.services.embeddings import generate_embedding


def retrieve_vector(
    db: Session,
    query: str,
    workspace_id: UUID,
    limit: int = 20,
) -> list[dict]:

    query = query.strip()

    if not query:
        return []

    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    statement = (
        select(
            DocumentChunk.id,
            DocumentChunk.text,
            DocumentPage.page_number,
            Document.id.label("document_id"),
            Document.title,
            distance.label("distance"),
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
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance)
        .limit(limit)
    )

    rows = db.execute(statement).all()

    results = []

    for rank, row in enumerate(rows, start=1):

        distance_value = float(row.distance)

        similarity = 1.0 - distance_value

        results.append(
            {
                "chunk_id": str(row.id),
                "document_id": str(row.document_id),
                "document_title": row.title,
                "page_number": row.page_number,
                "text": row.text,
                "vector_distance": round(
                    distance_value,
                    6,
                ),
                "vector_similarity": round(
                    similarity,
                    6,
                ),
                "vector_rank": rank,
                "rank": rank,
            }
        )

    return results