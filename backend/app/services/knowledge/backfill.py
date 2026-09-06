from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.page import DocumentPage
from app.services.knowledge.extractor import LLMKnowledgeExtractor
from app.services.knowledge.repository import persist_extraction


class KnowledgeBackfillService:

    def __init__(self) -> None:
        self.extractor = LLMKnowledgeExtractor()

    def process_document(
        self,
        db: Session,
        document_id: UUID,
    ) -> dict:

        document = db.get(
            Document,
            document_id,
        )

        if document is None:
            raise ValueError(
                "Document not found."
            )

        statement = (
            select(
                DocumentChunk
            )
            .join(
                DocumentPage,
                DocumentChunk.page_id
                == DocumentPage.id,
            )
            .where(
                DocumentPage.document_id
                == document_id
            )
            .order_by(
                DocumentPage.page_number,
                DocumentChunk.chunk_index,
            )
        )

        chunks = (
            db.execute(statement)
            .scalars()
            .all()
        )

        totals = {
            "chunks_processed": 0,
            "entities": 0,
            "claims": 0,
            "events": 0,
            "relationships": 0,
            "evidence": 0,
        }

        for chunk in chunks:

            text = chunk.text.strip()

            if not text:
                continue

            extraction = self.extractor.extract(
                text
            )

            result = persist_extraction(
                db=db,
                workspace_id=document.workspace_id,
                chunk_id=chunk.id,
                extraction=extraction,
            )

            totals["chunks_processed"] += 1

            totals["entities"] += result.get(
                "entities",
                0,
            )

            totals["claims"] += result.get(
                "claims",
                0,
            )

            totals["events"] += result.get(
                "events",
                0,
            )

            totals["relationships"] += result.get(
                "relationships",
                0,
            )

            totals["evidence"] += result.get(
                "evidence",
                0,
            )

        return {
            "document_id": str(document.id),
            "document_title": document.title,
            **totals,
        }

    def process_all_documents(
        self,
        db: Session,
    ) -> dict:

        documents = (
            db.execute(
                select(Document).order_by(
                    Document.created_at
                )
            )
            .scalars()
            .all()
        )

        totals = {
            "documents_processed": 0,
            "chunks_processed": 0,
            "entities": 0,
            "claims": 0,
            "events": 0,
            "relationships": 0,
            "evidence": 0,
        }

        document_results = []

        for document in documents:

            result = self.process_document(
                db=db,
                document_id=document.id,
            )

            document_results.append(result)

            totals["documents_processed"] += 1

            for key in (
                "chunks_processed",
                "entities",
                "claims",
                "events",
                "relationships",
                "evidence",
            ):
                totals[key] += result[key]

        return {
            **totals,
            "documents": document_results,
        }