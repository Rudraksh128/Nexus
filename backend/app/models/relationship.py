from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EntityRelationship(Base):
    __tablename__ = "entity_relationships"

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

    source_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "entities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    target_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "entities.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    relation_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    confidence: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    source_claim_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey(
            "claims.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )