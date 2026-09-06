from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.entity import Entity
from app.models.event import Event
from app.services.agent.tools.base import AgentTool


class TimelineTool(AgentTool):
    name = "timeline"
    description = (
        "Retrieve historical claims and events relevant to a topic. "
        "Use this when the question involves changes over time, historical "
        "comparisons, trends, or what changed between periods."
    )

    def run(
        self,
        db: Session,
        workspace_id,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        query = str(arguments.get("query", "")).strip()

        if not query:
            return {
                "success": False,
                "error": "Timeline query is required.",
            }

        pattern = f"%{query}%"

        claims_statement = (
            select(Claim)
            .where(
                Claim.workspace_id == workspace_id,
                or_(
                    Claim.predicate.ilike(pattern),
                    Claim.object_text.ilike(pattern),
                    Claim.normalized_value.ilike(pattern),
                ),
            )
            .order_by(
                Claim.valid_from.asc().nullsfirst(),
                Claim.created_at.asc(),
            )
            .limit(100)
        )

        claims = db.execute(claims_statement).scalars().all()

        events_statement = (
            select(Event)
            .where(
                Event.workspace_id == workspace_id,
                Event.description.ilike(pattern),
            )
            .order_by(
                Event.event_date.asc().nullsfirst(),
                Event.created_at.asc(),
            )
            .limit(100)
        )

        events = db.execute(events_statement).scalars().all()

        return {
            "success": True,
            "claims": [
                {
                    "id": str(claim.id),
                    "predicate": claim.predicate,
                    "object_text": claim.object_text,
                    "normalized_value": claim.normalized_value,
                    "value_unit": claim.value_unit,
                    "source_date": (
                        claim.source_date.isoformat()
                        if claim.source_date
                        else None
                    ),
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
                    "confidence": claim.confidence,
                }
                for claim in claims
            ],
            "events": [
                {
                    "id": str(event.id),
                    "event_type": event.event_type,
                    "description": event.description,
                    "event_date": (
                        event.event_date.isoformat()
                        if event.event_date
                        else None
                    ),
                    "confidence": event.confidence,
                }
                for event in events
            ],
        }