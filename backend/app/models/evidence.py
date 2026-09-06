from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    claim_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "claims.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    chunk_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "document_chunks.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    evidence_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    extraction_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="unknown",
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )