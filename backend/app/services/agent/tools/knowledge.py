from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.entity import Entity
from app.services.agent.tools.base import AgentTool


class KnowledgeTool(AgentTool):
    name = "knowledge"

    description = (
        "Inspect structured entities and claims stored in the NEXUS knowledge layer. "
        "Use this when the question concerns known facts, entities, relationships, "
        "or structured claims."
    )

    def run(
        self,
        db: Session,
        workspace_id,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        query = str(
            arguments.get("query")
            or arguments.get("entity")
            or ""
        ).strip()

        if not query:
            return {
                "success": False,
                "error": "Knowledge query is required.",
            }

        pattern = f"%{query}%"

        entity_statement = (
            select(Entity)
            .where(
                Entity.workspace_id == workspace_id,
                or_(
                    Entity.canonical_name.ilike(pattern),
                    Entity.description.ilike(pattern),
                ),
            )
            .limit(20)
        )

        entity_rows = (
            db.execute(entity_statement)
            .scalars()
            .all()
        )

        entity_ids = [entity.id for entity in entity_rows]

        conditions = [
            Claim.predicate.ilike(pattern),
            Claim.object_text.ilike(pattern),
            Claim.normalized_value.ilike(pattern),
        ]

        if entity_ids:
            conditions.extend(
                [
                    Claim.subject_entity_id.in_(entity_ids),
                    Claim.object_entity_id.in_(entity_ids),
                ]
            )

        claim_statement = (
            select(Claim)
            .where(
                Claim.workspace_id == workspace_id,
                or_(*conditions),
            )
            .limit(50)
        )

        claim_rows = (
            db.execute(claim_statement)
            .scalars()
            .all()
        )

        return {
            "success": True,
            "query": query,
            "entity_count": len(entity_rows),
            "claim_count": len(claim_rows),
            "entities": [
                {
                    "id": str(entity.id),
                    "name": entity.canonical_name,
                    "type": entity.entity_type,
                    "description": entity.description,
                }
                for entity in entity_rows
            ],
            "claims": [
                {
                    "id": str(claim.id),
                    "subject_entity_id": (
                        str(claim.subject_entity_id)
                        if claim.subject_entity_id
                        else None
                    ),
                    "object_entity_id": (
                        str(claim.object_entity_id)
                        if claim.object_entity_id
                        else None
                    ),
                    "predicate": claim.predicate,
                    "object_text": claim.object_text,
                    "value_type": claim.value_type,
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
                for claim in claim_rows
            ],
        }