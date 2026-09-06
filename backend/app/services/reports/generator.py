import json
from typing import Any

from app.services.knowledge.providers.base import BaseLLMProvider
from app.services.knowledge.providers.ollama_provider import OllamaProvider


REPORT_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "executive_summary": {
            "type": "string"
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "explanation": {
                        "type": "string"
                    },
                    "confidence": {
                        "type": "number"
                    }
                },
                "required": [
                    "title",
                    "explanation",
                    "confidence"
                ],
                "additionalProperties": False
            }
        },
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string"
                    },
                    "content": {
                        "type": "string"
                    }
                },
                "required": [
                    "title",
                    "content"
                ],
                "additionalProperties": False
            }
        },
        "evidence_indices": {
            "type": "array",
            "items": {
                "type": "integer"
            }
        },
        "confidence": {
            "type": "number"
        }
    },
    "required": [
        "title",
        "executive_summary",
        "findings",
        "sections",
        "evidence_indices",
        "confidence"
    ],
    "additionalProperties": False
}


SYSTEM_PROMPT = """
You are the research report generator for NEXUS.

Produce a professional research report using ONLY verified evidence.

Rules:

1. Never invent facts.
2. Never use outside knowledge.
3. Preserve names, dates, numbers and source titles.
4. Do not invent document identifiers or page numbers.
5. Distinguish direct evidence from interpretation.
6. Do not claim that evidence supports something unless it actually does.
7. If sources conflict, explicitly describe the conflict.
8. If evidence is insufficient, say so.
9. Keep findings concise and specific.
10. Evidence indices must refer only to supplied evidence.
11. Confidence must be between 0 and 1.
12. Do not call something a contradiction merely because two events
    occurred at different times.
"""


class ResearchReportGenerator:

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.provider = provider or OllamaProvider()

    def generate(
        self,
        question: str,
        evidence: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:

        if not evidence:
            return {
                "title": "Research Report",
                "executive_summary": (
                    "The available verified evidence is "
                    "insufficient to produce a reliable report."
                ),
                "findings": [],
                "sections": [],
                "evidence_indices": [],
                "confidence": 0.0,
            }

        payload = {
            "question": question,
            "verified_evidence": [
                {
                    "index": index,
                    "source_type": item.get("source_type"),
                    "document_title": item.get("document_title"),
                    "page_number": item.get("page_number"),
                    "text": item.get("text"),
                    "relevance": item.get("relevance"),
                }
                for index, item in enumerate(evidence)
            ],
            "context": context or {},
        }

        raw = self.provider.generate_structured(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            ),
            output_schema=REPORT_SCHEMA,
        )

        confidence = max(
            0.0,
            min(
                1.0,
                float(raw.get("confidence", 0.0)),
            ),
        )

        valid_indices = [
            index
            for index in raw.get(
                "evidence_indices",
                [],
            )
            if isinstance(index, int)
            and 0 <= index < len(evidence)
        ]

        return {
            "title": str(
                raw.get(
                    "title",
                    "Research Report",
                )
            ),
            "executive_summary": str(
                raw.get(
                    "executive_summary",
                    "",
                )
            ),
            "findings": raw.get(
                "findings",
                [],
            ),
            "sections": raw.get(
                "sections",
                [],
            ),
            "evidence_indices": valid_indices,
            "confidence": confidence,
        }