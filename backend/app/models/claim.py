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


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "workspaces.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    subject_entity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "entities.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    object_entity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "entities.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    predicate: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    object_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    value_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    normalized_value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    value_unit: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    valid_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    valid_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    extraction_method: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="unknown",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )