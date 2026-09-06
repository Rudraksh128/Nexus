from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.claim import Claim
from app.models.entity import Entity
from app.models.relationship import EntityRelationship
from app.services.knowledge.backfill import (
    KnowledgeBackfillService,
)


router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
)


@router.get("/graph")
def get_knowledge_graph(
    workspace_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Return the complete knowledge graph for a workspace.

    Nodes:
        Entities

    Edges:
        Entity relationships

    Additional metadata:
        Claims
    """

    entities = (
        db.execute(
            select(Entity)
            .where(
                Entity.workspace_id == workspace_id
            )
            .order_by(Entity.canonical_name)
        )
        .scalars()
        .all()
    )

    relationships = (
        db.execute(
            select(EntityRelationship)
            .where(
                EntityRelationship.workspace_id
                == workspace_id
            )
        )
        .scalars()
        .all()
    )

    claims = (
        db.execute(
            select(Claim)
            .where(
                Claim.workspace_id == workspace_id
            )
        )
        .scalars()
        .all()
    )

    entity_ids = {
        entity.id
        for entity in entities
    }

    nodes = []

    for entity in entities:
        nodes.append(
            {
                "id": str(entity.id),
                "label": entity.canonical_name,
                "type": entity.entity_type,
                "description": entity.description,
            }
        )

    edges = []

    for relationship in relationships:

        if (
            relationship.source_entity_id
            not in entity_ids
        ):
            continue

        if (
            relationship.target_entity_id
            not in entity_ids
        ):
            continue

        edges.append(
            {
                "id": str(relationship.id),
                "source": str(
                    relationship.source_entity_id
                ),
                "target": str(
                    relationship.target_entity_id
                ),
                "label": relationship.relation_type,
                "confidence": relationship.confidence,
                "source_claim_id": (
                    str(
                        relationship.source_claim_id
                    )
                    if relationship.source_claim_id
                    else None
                ),
            }
        )

    claim_data = []

    for claim in claims:
        claim_data.append(
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
                "normalized_value": (
                    claim.normalized_value
                ),
                "value_unit": claim.value_unit,
                "confidence": claim.confidence,
            }
        )

    return {
        "workspace_id": str(workspace_id),
        "nodes": nodes,
        "edges": edges,
        "claims": claim_data,
        "counts": {
            "nodes": len(nodes),
            "edges": len(edges),
            "claims": len(claim_data),
        },
    }


@router.post("/backfill")
def backfill_knowledge(
    db: Session = Depends(get_db),
):
    """
    Extract knowledge from all existing documents.

    Existing documents are processed through the
    NEXUS knowledge extraction pipeline.
    """

    service = KnowledgeBackfillService()

    try:
        result = service.process_all_documents(
            db=db,
        )

        db.commit()

        return {
            "success": True,
            **result,
        }

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Knowledge backfill failed: {exc}"
            ),
        )