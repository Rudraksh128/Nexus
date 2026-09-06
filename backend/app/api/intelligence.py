from collections import defaultdict
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.claim import Claim
from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.page import DocumentPage


router = APIRouter(
    prefix="/intelligence",
    tags=["Intelligence"],
)


# ============================================================
# EVIDENCE EXPLORER
# ============================================================

@router.get("/evidence")
def get_evidence(
    workspace_id: UUID,
    q: str = "",
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Return evidence items belonging only to the requested workspace.

    Evidence -> Claim
    Evidence -> Chunk -> Page -> Document
    """

    limit = max(1, min(limit, 200))
    query = q.strip()

    statement = (
        select(
            Evidence,
            Claim,
            Document,
            DocumentPage,
            DocumentChunk,
        )
        .join(
            Claim,
            Claim.id == Evidence.claim_id,
        )
        .join(
            DocumentChunk,
            DocumentChunk.id == Evidence.chunk_id,
        )
        .join(
            DocumentPage,
            DocumentPage.id == DocumentChunk.page_id,
        )
        .join(
            Document,
            Document.id == DocumentPage.document_id,
        )
        .where(
            Evidence.claim_id == Claim.id,
            Claim.workspace_id == workspace_id,
            Document.workspace_id == workspace_id,
        )
    )

    if query:
        pattern = f"%{query}%"

        statement = statement.where(
            or_(
                Evidence.evidence_text.ilike(pattern),
                Claim.predicate.ilike(pattern),
                Claim.object_text.ilike(pattern),
                Claim.normalized_value.ilike(pattern),
                Document.title.ilike(pattern),
            )
        )

    statement = (
        statement
        .order_by(Evidence.created_at.desc())
        .limit(limit)
    )

    rows = db.execute(statement).all()

    evidence = []

    for (
        evidence_row,
        claim,
        document,
        page,
        chunk,
    ) in rows:

        evidence.append(
            {
                "id": str(evidence_row.id),
                "claim_id": str(claim.id),
                "document_id": str(document.id),
                "document_title": document.title,
                "page_number": page.page_number,
                "chunk_id": str(chunk.id),
                "evidence_text": evidence_row.evidence_text,
                "claim": {
                    "predicate": claim.predicate,
                    "object_text": claim.object_text,
                    "normalized_value": claim.normalized_value,
                    "value_unit": claim.value_unit,
                    "confidence": claim.confidence,
                },
                "extraction_method": evidence_row.extraction_method,
                "confidence": evidence_row.confidence,
                "created_at": (
                    evidence_row.created_at.isoformat()
                    if evidence_row.created_at
                    else None
                ),
            }
        )

    return {
        "workspace_id": str(workspace_id),
        "query": query,
        "count": len(evidence),
        "evidence": evidence,
    }


# ============================================================
# TIMELINE
# ============================================================

@router.get("/timeline")
def get_timeline(
    workspace_id: UUID,
    q: str = "",
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Return chronological claims and events for a workspace.
    """

    limit = max(1, min(limit, 200))
    query = q.strip()

    pattern = f"%{query}%"

    claim_statement = (
        select(Claim)
        .where(
            Claim.workspace_id == workspace_id,
        )
    )

    if query:
        claim_statement = claim_statement.where(
            or_(
                Claim.predicate.ilike(pattern),
                Claim.object_text.ilike(pattern),
                Claim.normalized_value.ilike(pattern),
            )
        )

    claims = (
        db.execute(
            claim_statement
            .order_by(
                Claim.valid_from.asc().nullsfirst(),
                Claim.source_date.asc().nullsfirst(),
                Claim.created_at.asc(),
            )
            .limit(limit)
        )
        .scalars()
        .all()
    )

    event_statement = (
        select(Event)
        .where(
            Event.workspace_id == workspace_id,
        )
    )

    if query:
        event_statement = event_statement.where(
            or_(
                Event.event_type.ilike(pattern),
                Event.description.ilike(pattern),
            )
        )

    events = (
        db.execute(
            event_statement
            .order_by(
                Event.event_date.asc().nullsfirst(),
                Event.created_at.asc(),
            )
            .limit(limit)
        )
        .scalars()
        .all()
    )

    timeline = []

    for claim in claims:

        date_value = (
            claim.valid_from
            or claim.source_date
            or claim.created_at
        )

        timeline.append(
            {
                "id": str(claim.id),
                "type": "claim",
                "date": (
                    date_value.isoformat()
                    if date_value
                    else None
                ),
                "title": claim.predicate,
                "description": (
                    claim.object_text
                    or claim.normalized_value
                    or ""
                ),
                "confidence": claim.confidence,
                "valid_from": (
                    claim.valid_from.isoformat()
                    if claim.valid_from
                    else None
                ),
                "valid_until": (
                    claim.valid_until.isoformat()
                    if claim.valid_until
                    else None
                ),
            }
        )

    for event in events:

        timeline.append(
            {
                "id": str(event.id),
                "type": "event",
                "date": (
                    event.event_date.isoformat()
                    if event.event_date
                    else None
                ),
                "title": event.event_type,
                "description": event.description,
                "confidence": event.confidence,
                "valid_from": None,
                "valid_until": None,
            }
        )

    timeline.sort(
        key=lambda item: item["date"] or "9999-12-31"
    )

    return {
        "workspace_id": str(workspace_id),
        "query": query,
        "count": len(timeline),
        "timeline": timeline[:limit],
    }


# ============================================================
# CONTRADICTION DETECTION
# ============================================================

@router.get("/contradictions")
def get_contradictions(
    workspace_id: UUID,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Detect potentially contradictory claims.

    Claims are compared when they describe the same subject
    and predicate but contain different values.
    """

    limit = max(1, min(limit, 200))

    claims = (
        db.execute(
            select(Claim)
            .where(
                Claim.workspace_id == workspace_id,
                Claim.subject_entity_id.is_not(None),
                or_(
                    Claim.object_text.is_not(None),
                    Claim.normalized_value.is_not(None),
                ),
            )
            .order_by(
                Claim.created_at.asc()
            )
            .limit(1000)
        )
        .scalars()
        .all()
    )

    groups = defaultdict(list)

    for claim in claims:

        key = (
            str(claim.subject_entity_id),
            claim.predicate.strip().lower(),
        )

        value = (
            claim.normalized_value
            or claim.object_text
            or ""
        ).strip()

        if value:
            groups[key].append(
                {
                    "id": str(claim.id),
                    "predicate": claim.predicate,
                    "value": value,
                    "confidence": claim.confidence,
                    "valid_from": (
                        claim.valid_from.isoformat()
                        if claim.valid_from
                        else None
                    ),
                    "valid_until": (
                        claim.valid_until.isoformat()
                        if claim.valid_until
                        else None
                    ),
                }
            )

    contradictions = []

    for (
        subject_id,
        predicate,
    ), group in groups.items():

        unique_values = {}

        for item in group:
            normalized = item["value"].strip().lower()

            if normalized not in unique_values:
                unique_values[normalized] = item

        values = list(unique_values.values())

        if len(values) < 2:
            continue

        for index in range(len(values) - 1):

            first = values[index]
            second = values[index + 1]

            confidence_values = [
                value
                for value in [
                    first.get("confidence"),
                    second.get("confidence"),
                ]
                if value is not None
            ]

            confidence = (
                sum(confidence_values)
                / len(confidence_values)
                if confidence_values
                else None
            )

            contradictions.append(
                {
                    "id": (
                        f"{first['id']}-{second['id']}"
                    ),
                    "subject_entity_id": subject_id,
                    "predicate": predicate,
                    "claim_a": first,
                    "claim_b": second,
                    "confidence": confidence,
                }
            )

    contradictions.sort(
        key=lambda item: (
            -(item["confidence"] or 0)
        )
    )

    return {
        "workspace_id": str(workspace_id),
        "count": len(contradictions[:limit]),
        "contradictions": contradictions[:limit],
    }