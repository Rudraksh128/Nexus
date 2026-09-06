import hashlib
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy import distinct, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.models.page import DocumentPage
from app.services.chunker import chunk_text
from app.services.embeddings import generate_embedding
from app.services.ingestion.parser import (
    is_supported_file,
    parse_document,
)
from app.services.knowledge.backfill import (
    KnowledgeBackfillService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("storage/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


@router.get("")
def list_documents(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    """Return indexed documents and their ingestion totals."""

    rows = (
        db.execute(
            select(
                Document,
                func.count(distinct(DocumentPage.id)).label("pages"),
                func.count(DocumentChunk.id).label("chunks"),
            )
            .outerjoin(
                DocumentPage,
                DocumentPage.document_id == Document.id,
            )
            .outerjoin(
                DocumentChunk,
                DocumentChunk.page_id == DocumentPage.id,
            )
            .where(Document.workspace_id == workspace_id)
            .group_by(Document.id)
            .order_by(Document.created_at.desc())
        )
        .all()
    )

    documents = [
        {
            "id": str(document.id),
            "title": document.title,
            "source_type": document.source_type,
            "created_at": document.created_at.isoformat(),
            "pages": pages,
            "chunks": chunks,
        }
        for document, pages, chunks in rows
    ]

    return {
        "workspace_id": str(workspace_id),
        "documents": documents,
        "count": len(documents),
    }


@router.post("/upload")
async def upload_document(
    workspace_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Universal document ingestion endpoint.

    Supported formats:
        PDF
        TXT
        MD
        DOCX
        CSV
        JSON
        XLSX

    Processing pipeline:

        Source file
             ↓
        Parser
             ↓
        Normalized pages
             ↓
        Chunks
             ↓
        Embeddings
             ↓
        PostgreSQL + pgvector
             ↓
        Knowledge extraction
             ↓
        Entities + Claims + Relationships + Events + Evidence
    """

    filename = file.filename or "untitled"

    # ---------------------------------------------------------
    # 1. Validate file type
    # ---------------------------------------------------------
    if not is_supported_file(filename):
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. Supported formats: "
                "PDF, TXT, MD, DOCX, CSV, JSON, XLSX."
            ),
        )

    # ---------------------------------------------------------
    # 2. Read uploaded file
    # ---------------------------------------------------------
    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    # ---------------------------------------------------------
    # 3. Generate file hash
    # ---------------------------------------------------------
    file_hash = hashlib.sha256(
        contents
    ).hexdigest()

    # ---------------------------------------------------------
    # 4. Duplicate detection
    # ---------------------------------------------------------
    existing_document = db.execute(
        select(Document).where(
            Document.workspace_id == workspace_id,
            Document.file_hash == file_hash,
        )
    ).scalar_one_or_none()

    if existing_document:
        return {
            "status": "already_exists",
            "document_id": str(
                existing_document.id
            ),
            "filename": existing_document.title,
            "message": (
                "This document has already been indexed."
            ),
        }

    # ---------------------------------------------------------
    # 5. Create storage path
    # ---------------------------------------------------------
    document_id = uuid4()

    extension = Path(filename).suffix.lower()

    file_path = (
        UPLOAD_DIR
        / f"{document_id}{extension}"
    )

    try:

        # -----------------------------------------------------
        # 6. Save original file
        # -----------------------------------------------------
        file_path.write_bytes(contents)

        # -----------------------------------------------------
        # 7. Parse document
        # -----------------------------------------------------
        pages = parse_document(
            file_path=file_path,
            filename=filename,
        )

        if not pages:
            raise HTTPException(
                status_code=400,
                detail=(
                    "The document contains no "
                    "extractable content."
                ),
            )

        # -----------------------------------------------------
        # 8. Create document record
        # -----------------------------------------------------
        document = Document(
            id=document_id,
            workspace_id=workspace_id,
            title=filename,
            source_type=extension.lstrip("."),
            source_uri=str(file_path),
            file_hash=file_hash,
        )

        db.add(document)

        total_chunks = 0
        total_embeddings = 0

        # -----------------------------------------------------
        # 9. Process normalized pages
        # -----------------------------------------------------
        for parsed_page in pages:

            page = DocumentPage(
                document_id=document_id,
                page_number=parsed_page.page_number,
                text=parsed_page.text,
            )

            db.add(page)
            db.flush()

            # -------------------------------------------------
            # 10. Chunk page
            # -------------------------------------------------
            chunks = chunk_text(
                parsed_page.text
            )

            # -------------------------------------------------
            # 11. Generate embeddings
            # -------------------------------------------------
            for index, chunk in enumerate(chunks):

                embedding = generate_embedding(
                    chunk
                )

                chunk_record = DocumentChunk(
                    page_id=page.id,
                    chunk_index=index,
                    text=chunk,
                    embedding=embedding,
                )

                db.add(chunk_record)

                total_chunks += 1
                total_embeddings += 1

        # -----------------------------------------------------
        # 12. Commit document/indexing transaction
        # -----------------------------------------------------
        db.commit()

        # -----------------------------------------------------
        # 13. Knowledge extraction
        # -----------------------------------------------------
        knowledge_result = (
            KnowledgeBackfillService().process_document(
                db=db,
                document_id=document_id,
            )
        )

        # -----------------------------------------------------
        # 14. Commit extracted knowledge
        # -----------------------------------------------------
        db.commit()

        # -----------------------------------------------------
        # 15. Return complete ingestion result
        # -----------------------------------------------------
        return {
            "status": "ingested",
            "document_id": str(
                document_id
            ),
            "filename": filename,
            "source_type": extension.lstrip("."),
            "pages": len(pages),
            "chunks": total_chunks,
            "embeddings": total_embeddings,
            "embedding_dimensions": 384,
            "file_hash": file_hash,
            "knowledge": knowledge_result,
        }

    # ---------------------------------------------------------
    # Expected HTTP errors
    # ---------------------------------------------------------
    except HTTPException:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise

    # ---------------------------------------------------------
    # Database integrity errors
    # ---------------------------------------------------------
    except IntegrityError:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        existing_document = db.execute(
            select(Document).where(
                Document.workspace_id == workspace_id,
                Document.file_hash == file_hash,
            )
        ).scalar_one_or_none()

        if existing_document:
            return {
                "status": "already_exists",
                "document_id": str(
                    existing_document.id
                ),
                "filename": existing_document.title,
                "message": (
                    "This document has already "
                    "been indexed."
                ),
            }

        raise HTTPException(
            status_code=409,
            detail=(
                "Document could not be indexed "
                "because it conflicts with an "
                "existing document."
            ),
        )

    # ---------------------------------------------------------
    # Unexpected errors
    # ---------------------------------------------------------
    except Exception:

        db.rollback()

        if file_path.exists():
            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Document ingestion failed.",
        )
