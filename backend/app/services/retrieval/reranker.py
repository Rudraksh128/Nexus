# app/services/retrieval/reranker.py

from abc import ABC, abstractmethod

from sentence_transformers import CrossEncoder

from app.services.retrieval.schemas import RetrievalCandidate


class BaseReranker(ABC):

    @abstractmethod
    def rerank(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        limit: int = 5,
    ) -> list[RetrievalCandidate]:
        raise NotImplementedError


class RRFReranker(BaseReranker):

    def rerank(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        limit: int = 5,
    ) -> list[RetrievalCandidate]:

        if not candidates:
            return []

        ranked = sorted(
            candidates,
            key=lambda candidate: (
                candidate.rrf_score or 0.0
            ),
            reverse=True,
        )

        for rank, candidate in enumerate(
            ranked,
            start=1,
        ):
            candidate.rrf_rank = rank
            candidate.rerank_score = candidate.rrf_score

        return ranked[:limit]


class CrossEncoderReranker(BaseReranker):

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self) -> None:
        self.model = CrossEncoder(self.MODEL_NAME)

    def rerank(
        self,
        query: str,
        candidates: list[RetrievalCandidate],
        limit: int = 5,
    ) -> list[RetrievalCandidate]:

        if not candidates:
            return []

        pairs = [
            (query, candidate.text)
            for candidate in candidates
        ]

        scores = self.model.predict(
            pairs,
            show_progress_bar=False,
        )

        for candidate, score in zip(candidates, scores):
            candidate.rerank_score = float(score)

        ranked = sorted(
            candidates,
            key=lambda candidate: (
                candidate.rerank_score
                if candidate.rerank_score is not None
                else float("-inf")
            ),
            reverse=True,
        )

        for rank, candidate in enumerate(
            ranked,
            start=1,
        ):
            candidate.rrf_rank = rank

        return ranked[:limit]


def create_reranker(
    reranker_name: str,
) -> BaseReranker:

    name = reranker_name.strip().lower()

    if name == "rrf":
        return RRFReranker()

    if name == "cross_encoder":
        return CrossEncoderReranker()

    raise ValueError(
        f"Unsupported reranker: {reranker_name}. "
        "Expected 'rrf' or 'cross_encoder'."
    )