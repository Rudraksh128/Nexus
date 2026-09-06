from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.agent.orchestrator import ResearchAgent


router = APIRouter(
    prefix="/research",
    tags=["Research"],
)


class ResearchRequest(BaseModel):

    workspace_id: UUID

    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
    )


@router.post("")
def research(
    request: ResearchRequest,
    db: Session = Depends(get_db),
):

    try:

        agent = ResearchAgent()

        result = agent.research(
            db=db,
            workspace_id=request.workspace_id,
            question=request.question,
        )

        return {
            "question": result.question,
            "answer": result.answer,
            "confidence": result.confidence,

            "steps": [
                {
                    "tool": step.tool,
                    "reason": step.reason,
                    "arguments": step.arguments,
                }
                for step in result.steps
            ],

            "trace": [
                {
                    "step_number": event.step_number,
                    "action": event.action,
                    "tool": event.tool,
                    "reason": event.reason,
                    "outcome": event.outcome,
                }
                for event in result.trace
            ],

            "evidence": [
                {
                    "source_type": item.source_type,
                    "document_id": item.document_id,
                    "document_title": item.document_title,
                    "page_number": item.page_number,
                    "text": item.text,
                    "relevance": item.relevance,
                    "metadata": item.metadata,
                }
                for item in result.evidence
            ],

            "tool_results": [
                {
                    "tool": item.tool,
                    "success": item.success,
                    "data": item.data,
                    "error": item.error,
                }
                for item in result.tool_results
            ],
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc