from typing import Any

from sqlalchemy.orm import Session

from app.services.agent.orchestrator import ResearchAgent
from app.services.reports.generator import ResearchReportGenerator


class ResearchReportService:

    def __init__(self) -> None:
        self.agent = ResearchAgent()
        self.generator = ResearchReportGenerator()

    def generate_report(
        self,
        db: Session,
        workspace_id,
        question: str,
    ) -> dict[str, Any]:

        research = self.agent.research(
            db=db,
            workspace_id=workspace_id,
            question=question,
        )

        evidence = [
            {
                "source_type": item.source_type,
                "document_id": item.document_id,
                "document_title": item.document_title,
                "page_number": item.page_number,
                "text": item.text,
                "relevance": item.relevance,
                "metadata": item.metadata,
            }
            for item in research.evidence
        ]

        report = self.generator.generate(
            question=question,
            evidence=evidence,
            context={
                "research_confidence": research.confidence,
                "trace": [
                    {
                        "step_number": event.step_number,
                        "action": event.action,
                        "tool": event.tool,
                        "reason": event.reason,
                        "outcome": event.outcome,
                    }
                    for event in research.trace
                ],
            },
        )

        selected_indices = set(
            report.get(
                "evidence_indices",
                [],
            )
        )

        report_evidence = [
            item
            for index, item in enumerate(evidence)
            if index in selected_indices
        ]

        return {
            "title": report["title"],
            "question": question,
            "executive_summary": report[
                "executive_summary"
            ],
            "findings": report["findings"],
            "sections": report["sections"],
            "evidence": report_evidence,
            "confidence": report["confidence"],
            "research_trace": [
                {
                    "step_number": event.step_number,
                    "action": event.action,
                    "tool": event.tool,
                    "reason": event.reason,
                    "outcome": event.outcome,
                }
                for event in research.trace
            ],
        }