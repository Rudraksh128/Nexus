from sqlalchemy.orm import Session

from app.services.agent.loop import AgentLoop
from app.services.agent.schemas import (
    ResearchEvidence,
    ResearchResult,
)
from app.services.agent.synthesizer import ResearchSynthesizer
from app.services.agent.verifier import EvidenceVerifier


class ResearchAgent:

    def __init__(self) -> None:

        self.loop = AgentLoop()
        self.verifier = EvidenceVerifier()
        self.synthesizer = ResearchSynthesizer()

    def research(
        self,
        db: Session,
        workspace_id,
        question: str,
    ) -> ResearchResult:

        question = question.strip()

        if not question:
            raise ValueError(
                "Research question cannot be empty."
            )

        # ---------------------------------------------------------
        # 1. ITERATIVE RESEARCH LOOP
        # ---------------------------------------------------------
        (
            steps,
            trace,
            tool_results,
        ) = self.loop.run(
            db=db,
            workspace_id=workspace_id,
            question=question,
        )

        # ---------------------------------------------------------
        # 2. VERIFY EVIDENCE
        # ---------------------------------------------------------
        verification = self.verifier.verify(
            question=question,
            tool_results=tool_results,
        )

        verified_evidence = verification[
            "evidence"
        ]

        # ---------------------------------------------------------
        # 3. SYNTHESIZE FROM VERIFIED EVIDENCE ONLY
        # ---------------------------------------------------------
        synthesis = self.synthesizer.synthesize(
            question=question,
            evidence=verified_evidence,
        )

        selected_indices = set(
            synthesis.get(
                "evidence_indices",
                [],
            )
        )

        research_evidence = []

        for index, item in enumerate(
            verified_evidence
        ):

            if index not in selected_indices:
                continue

            research_evidence.append(
                ResearchEvidence(
                    source_type=item[
                        "source_type"
                    ],
                    document_id=item.get(
                        "document_id"
                    ),
                    document_title=item.get(
                        "document_title"
                    ),
                    page_number=item.get(
                        "page_number"
                    ),
                    text=item[
                        "text"
                    ],
                    relevance=item.get(
                        "relevance"
                    ),
                    metadata=item.get(
                        "metadata",
                        {},
                    ),
                )
            )

        return ResearchResult(
            question=question,
            answer=synthesis.get(
                "answer",
                (
                    "The available evidence is "
                    "insufficient to answer this confidently."
                ),
            ),
            steps=steps,
            trace=trace,
            evidence=research_evidence,
            tool_results=tool_results,
            confidence=float(
                synthesis.get(
                    "confidence",
                    0.0,
                )
            ),
        )