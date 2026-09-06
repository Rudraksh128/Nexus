# app/services/agent/tools/search.py

from typing import Any

from sqlalchemy.orm import Session

from app.services.agent.tools.base import AgentTool
from app.services.retriever import search_chunks


class SearchTool(AgentTool):

    name = "search"

    description = (
        "Search documents using hybrid semantic and lexical retrieval. "
        "Use this when factual evidence needs to be found inside documents."
    )

    def run(
        self,
        db: Session,
        workspace_id,
        arguments: dict[str, Any],
    ) -> dict[str, Any]:

        query = str(
            arguments.get("query", "")
        ).strip()

        if not query:
            return {
                "success": False,
                "error": "Search query is required.",
            }

        try:
            limit = int(
                arguments.get("limit", 5)
            )
        except (TypeError, ValueError):
            limit = 5

        limit = max(
            1,
            min(limit, 10),
        )

        results = search_chunks(
            db=db,
            query=query,
            workspace_id=workspace_id,
            limit=limit,
        )

        formatted = []

        for result in results:
            formatted.append(
                {
                    "chunk_id": str(result.chunk_id),
                    "document_id": str(result.document_id),
                    "document_title": result.document_title,
                    "page_number": result.page_number,
                    "text": result.text,
                    "vector_similarity": result.vector_similarity,
                    "lexical_score": result.lexical_score,
                    "rrf_score": result.rrf_score,
                    "rerank_score": result.rerank_score,
                    "retrieval_sources": result.retrieval_sources,
                }
            )

        return {
            "success": True,
            "query": query,
            "count": len(formatted),
            "results": formatted,
        }