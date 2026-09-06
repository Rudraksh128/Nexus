from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "file_hash",
            name="uq_documents_workspace_file_hash",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    source_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    file_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )