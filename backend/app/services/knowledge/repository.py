from uuid import UUID

from sqlalchemy.orm import Session

from app.models.claim import Claim
from app.models.entity import Entity
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.relationship import EntityRelationship
from app.services.knowledge.schemas import KnowledgeExtractionResult


EXTRACTION_METHOD = "ollama_qwen3"


def _find_or_create_entity(
    db: Session,
    workspace_id: UUID,
    name: str,
    entity_type: str,
    description: str | None = None,
) -> Entity:

    normalized_name = name.strip()

    existing = (
        db.query(Entity)
        .filter(
            Entity.workspace_id == workspace_id,
            Entity.canonical_name.ilike(normalized_name),
        )
        .first()
    )

    if existing:
        if description:
            existing.description = description
        if entity_type:
            existing.entity_type = entity_type
        db.flush()
        return existing

    entity = Entity(
        workspace_id=workspace_id,
        canonical_name=normalized_name,
        entity_type=entity_type,
        description=description,
    )

    db.add(entity)
    db.flush()

    return entity


def persist_extraction(
    db: Session,
    workspace_id: UUID,
    chunk_id: UUID,
    extraction: KnowledgeExtractionResult,
) -> dict:

    entity_map: dict[str, Entity] = {}

    # ---------------------------------------------------------
    # 1. Persist entities
    # ---------------------------------------------------------
    for extracted_entity in extraction.entities:

        name = extracted_entity.name.strip()

        if not name:
            continue

        key = name.lower()

        entity = _find_or_create_entity(
            db=db,
            workspace_id=workspace_id,
            name=name,
            entity_type=extracted_entity.entity_type,
            description=extracted_entity.description,
        )

        entity_map[key] = entity

    # ---------------------------------------------------------
    # 2. Persist claims + evidence
    # ---------------------------------------------------------
    created_claims = 0
    created_evidence = 0

    for extracted_claim in extraction.claims:

        subject_name = extracted_claim.subject.strip()

        subject = entity_map.get(
            subject_name.lower()
        )

        claim = Claim(
            workspace_id=workspace_id,
            subject_entity_id=(
                subject.id
                if subject
                else None
            ),
            predicate=extracted_claim.predicate.strip(),
            object_text=extracted_claim.object_text,
            value_type=extracted_claim.value_type,
            normalized_value=(
                extracted_claim.normalized_value
            ),
            value_unit=extracted_claim.value_unit,
            confidence=extracted_claim.confidence,
            extraction_method=EXTRACTION_METHOD,
        )

        db.add(claim)
        db.flush()

        created_claims += 1

        # Evidence currently points to the source chunk.
        # Later, we can add sentence-level spans.
        evidence_text = (
            f"{subject_name} "
            f"{extracted_claim.predicate.strip()}: "
            f"{extracted_claim.object_text or extracted_claim.normalized_value or ''}"
        ).strip()

        evidence = Evidence(
            claim_id=claim.id,
            chunk_id=chunk_id,
            evidence_text=evidence_text,
            extraction_method=EXTRACTION_METHOD,
            confidence=extracted_claim.confidence,
        )

        db.add(evidence)
        created_evidence += 1

    # ---------------------------------------------------------
    # 3. Persist events
    # ---------------------------------------------------------
    created_events = 0

    for extracted_event in extraction.events:

        description = extracted_event.description.strip()

        if not description:
            continue

        event = Event(
            workspace_id=workspace_id,
            event_type=(
                extracted_event.event_type.strip()
            ),
            description=description,
            source_chunk_id=chunk_id,
            confidence=extracted_event.confidence,
        )

        db.add(event)
        created_events += 1

    # ---------------------------------------------------------
    # 4. Persist relationships
    # ---------------------------------------------------------
    created_relationships = 0

    for extracted_relationship in extraction.relationships:

        source = entity_map.get(
            extracted_relationship.source_entity
            .strip()
            .lower()
        )

        target = entity_map.get(
            extracted_relationship.target_entity
            .strip()
            .lower()
        )

        if not source or not target:
            continue

        relationship = EntityRelationship(
            workspace_id=workspace_id,
            source_entity_id=source.id,
            target_entity_id=target.id,
            relation_type=(
                extracted_relationship.relation_type.strip()
            ),
            confidence=(
                extracted_relationship.confidence
            ),
        )

        db.add(relationship)
        created_relationships += 1

    db.commit()

    return {
        "entities": len(entity_map),
        "claims": created_claims,
        "events": created_events,
        "relationships": created_relationships,
        "evidence": created_evidence,
    }