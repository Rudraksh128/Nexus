from dataclasses import dataclass, field


@dataclass
class ExtractedEntity:
    name: str
    entity_type: str
    description: str | None = None


@dataclass
class ExtractedClaim:
    subject: str
    predicate: str
    object_text: str | None = None
    value_type: str | None = None
    normalized_value: str | None = None
    value_unit: str | None = None
    confidence: float = 0.5


@dataclass
class ExtractedEvent:
    event_type: str
    description: str
    confidence: float = 0.5


@dataclass
class ExtractedRelationship:
    source_entity: str
    target_entity: str
    relation_type: str
    confidence: float = 0.5


@dataclass
class KnowledgeExtractionResult:
    entities: list[ExtractedEntity] = field(
        default_factory=list
    )

    claims: list[ExtractedClaim] = field(
        default_factory=list
    )

    events: list[ExtractedEvent] = field(
        default_factory=list
    )

    relationships: list[ExtractedRelationship] = field(
        default_factory=list
    )