from app.core.config import settings

from app.services.knowledge.providers.base import (
    BaseLLMProvider,
)
from app.services.knowledge.providers.ollama_provider import (
    OllamaProvider,
)
from app.services.knowledge.schemas import (
    ExtractedClaim,
    ExtractedEntity,
    ExtractedEvent,
    ExtractedRelationship,
    KnowledgeExtractionResult,
)


KNOWLEDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "entity_type": {
                        "type": "string",
                    },
                    "description": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                },
                "required": [
                    "name",
                    "entity_type",
                    "description",
                ],
                "additionalProperties": False,
            },
        },
        "claims": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "subject": {
                        "type": "string",
                    },
                    "predicate": {
                        "type": "string",
                    },
                    "object_text": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                    "value_type": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                    "normalized_value": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                    "value_unit": {
                        "type": [
                            "string",
                            "null",
                        ],
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
                "required": [
                    "subject",
                    "predicate",
                    "object_text",
                    "value_type",
                    "normalized_value",
                    "value_unit",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
        "events": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "event_type": {
                        "type": "string",
                    },
                    "description": {
                        "type": "string",
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
                "required": [
                    "event_type",
                    "description",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source_entity": {
                        "type": "string",
                    },
                    "target_entity": {
                        "type": "string",
                    },
                    "relation_type": {
                        "type": "string",
                    },
                    "confidence": {
                        "type": "number",
                    },
                },
                "required": [
                    "source_entity",
                    "target_entity",
                    "relation_type",
                    "confidence",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": [
        "entities",
        "claims",
        "events",
        "relationships",
    ],
    "additionalProperties": False,
}


SYSTEM_PROMPT = """
You are the structured knowledge extraction engine for NEXUS.

Extract only information explicitly supported by the source text.

NEVER invent facts.

Extract:

1. Entities
   - people
   - organizations
   - locations
   - roles
   - products
   - other meaningful named entities

2. Claims
   Represent factual statements from the source.

3. Events
   Extract explicit events and actions.

4. Relationships
   Extract relationships explicitly supported by the text.

Rules:

- Preserve important names exactly.
- Preserve numerical values exactly when possible.
- Do not infer unstated information.
- Do not combine unrelated facts.
- Confidence describes extraction confidence,
  not truth of the real-world claim.
- Return only information supported by the supplied text.
"""


class LLMKnowledgeExtractor:
    """
    Provider-independent structured knowledge extractor.
    """

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:

        self.provider = (
            provider
            if provider is not None
            else self._create_provider()
        )

    @staticmethod
    def _create_provider() -> BaseLLMProvider:
        provider_name = (
            settings.LLM_PROVIDER.strip().lower()
        )

        if provider_name == "ollama":
            return OllamaProvider(
                model=settings.LLM_MODEL
            )

        raise ValueError(
            f"Unsupported LLM provider: "
            f"{settings.LLM_PROVIDER}"
        )

    def extract(
        self,
        text: str,
    ) -> KnowledgeExtractionResult:

        text = text.strip()

        if not text:
            return KnowledgeExtractionResult()

        raw = self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=text,
            output_schema=KNOWLEDGE_SCHEMA,
        )

        return KnowledgeExtractionResult(
            entities=[
                ExtractedEntity(
                    name=item["name"],
                    entity_type=item["entity_type"],
                    description=item["description"],
                )
                for item in raw.get(
                    "entities",
                    [],
                )
            ],
            claims=[
                ExtractedClaim(
                    subject=item["subject"],
                    predicate=item["predicate"],
                    object_text=item[
                        "object_text"
                    ],
                    value_type=item[
                        "value_type"
                    ],
                    normalized_value=item[
                        "normalized_value"
                    ],
                    value_unit=item[
                        "value_unit"
                    ],
                    confidence=item[
                        "confidence"
                    ],
                )
                for item in raw.get(
                    "claims",
                    [],
                )
            ],
            events=[
                ExtractedEvent(
                    event_type=item[
                        "event_type"
                    ],
                    description=item[
                        "description"
                    ],
                    confidence=item[
                        "confidence"
                    ],
                )
                for item in raw.get(
                    "events",
                    [],
                )
            ],
            relationships=[
                ExtractedRelationship(
                    source_entity=item[
                        "source_entity"
                    ],
                    target_entity=item[
                        "target_entity"
                    ],
                    relation_type=item[
                        "relation_type"
                    ],
                    confidence=item[
                        "confidence"
                    ],
                )
                for item in raw.get(
                    "relationships",
                    [],
                )
            ],
        )


def create_llm_extractor() -> LLMKnowledgeExtractor:
    return LLMKnowledgeExtractor()