# app/services/retrieval/fusion.py

from typing import Any

from app.services.retrieval.schemas import RetrievalCandidate


RRF_K = 60


def _rrf_score(rank: int) -> float:
    return 1.0 / (RRF_K + rank)


def reciprocal_rank_fusion(
    result_lists: list[list[dict[str, Any]]],
    limit: int = 5,
) -> list[RetrievalCandidate]:

    if not result_lists:
        return []

    candidates: dict[str, RetrievalCandidate] = {}

    for result_list in result_lists:
        for result in result_list:

            chunk_id = str(result["chunk_id"])

            if chunk_id not in candidates:
                candidates[chunk_id] = RetrievalCandidate(
                    chunk_id=chunk_id,
                    document_id=str(result["document_id"]),
                    document_title=result["document_title"],
                    page_number=int(result["page_number"]),
                    text=result["text"],
                )

            candidate = candidates[chunk_id]

            rank = int(result["rank"])

            candidate.rrf_score = (
                candidate.rrf_score or 0.0
            ) + _rrf_score(rank)

            if "vector_similarity" in result:
                candidate.vector_similarity = float(
                    result["vector_similarity"]
                )
                candidate.vector_rank = int(
                    result["vector_rank"]
                )

                if "vector" not in candidate.retrieval_sources:
                    candidate.retrieval_sources.append("vector")

            if "lexical_score" in result:
                candidate.lexical_score = float(
                    result["lexical_score"]
                )
                candidate.lexical_rank = int(
                    result["lexical_rank"]
                )

                if "lexical" not in candidate.retrieval_sources:
                    candidate.retrieval_sources.append("lexical")

    ranked_candidates = sorted(
        candidates.values(),
        key=lambda candidate: (
            candidate.rrf_score or 0.0
        ),
        reverse=True,
    )

    for rank, candidate in enumerate(
        ranked_candidates,
        start=1,
    ):
        candidate.rrf_rank = rank

        if candidate.rrf_score is not None:
            candidate.rrf_score = round(
                candidate.rrf_score,
                6,
            )

    return ranked_candidates[:limit]