from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DecisionDependency(Base):
    __tablename__ = "decision_dependencies"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    decision_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("decisions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    assumption_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("assumptions.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    claim_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("claims.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    dependency_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
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