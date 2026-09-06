import json
from typing import Any

from app.services.knowledge.providers.base import BaseLLMProvider
from app.services.knowledge.providers.ollama_provider import OllamaProvider


SYNTHESIS_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
        },
        "confidence": {
            "type": "number",
        },
        "evidence_indices": {
            "type": "array",
            "items": {
                "type": "integer",
            },
        },
    },
    "required": [
        "answer",
        "confidence",
        "evidence_indices",
    ],
    "additionalProperties": False,
}


SYSTEM_PROMPT = """
You are the final research synthesizer for NEXUS.

You receive VERIFIED EVIDENCE selected by the NEXUS evidence verifier.

Answer the user's question using ONLY this verified evidence.

Rules:

1. Never invent facts.
2. Never use outside knowledge.
3. Do not refer to a source using invented names such as
   "Document 5" unless that exact name exists in the evidence.
4. When citing a document, use its exact document_title and page_number.
5. Distinguish source facts from interpretation.
6. If sources disagree, explicitly state that they disagree.
7. If evidence is insufficient, explicitly say:
   "The available evidence is insufficient to answer this confidently."
8. Do not claim that something is supported unless it appears in the
   supplied evidence.
9. Confidence must reflect the strength and completeness of the supplied
   evidence.
10. evidence_indices must contain only indices from the supplied evidence.
11. Return only the requested structured JSON.
"""


class ResearchSynthesizer:

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.provider = provider or OllamaProvider()

    def synthesize(
        self,
        question: str,
        evidence: list[dict[str, Any]],
    ) -> dict[str, Any]:

        # The synthesizer receives VERIFIED evidence only.
        payload = {
            "question": question,
            "verified_evidence": [
                {
                    "index": index,
                    "source_type": item.get("source_type"),
                    "document_title": item.get(
                        "document_title"
                    ),
                    "page_number": item.get(
                        "page_number"
                    ),
                    "text": item.get("text"),
                    "relevance": item.get(
                        "relevance"
                    ),
                }
                for index, item in enumerate(evidence)
            ],
        }

        # No verified evidence means the LLM must not manufacture an answer.
        if not evidence:

            return {
                "answer": (
                    "The available evidence is insufficient "
                    "to answer this confidently."
                ),
                "confidence": 0.0,
                "evidence_indices": [],
            }

        raw = self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            ),
            output_schema=SYNTHESIS_SCHEMA,
        )

        confidence = float(
            raw.get("confidence", 0.0)
        )

        confidence = max(
            0.0,
            min(1.0, confidence),
        )

        valid_indices = []

        for index in raw.get(
            "evidence_indices",
            [],
        ):

            if isinstance(index, int) and 0 <= index < len(evidence):
                valid_indices.append(index)

        return {
            "answer": str(
                raw.get(
                    "answer",
                    "The available evidence is insufficient to answer this confidently.",
                )
            ),
            "confidence": confidence,
            "evidence_indices": valid_indices,
        }