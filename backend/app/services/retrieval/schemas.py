from dataclasses import dataclass, field
from typing import Any


@dataclass
class RetrievalCandidate:
    """
    Standard representation of evidence retrieved by NEXUS.
    """

    chunk_id: str
    document_id: str
    document_title: str
    page_number: int
    text: str

    # Retrieval scores
    vector_similarity: float | None = None
    lexical_score: float | None = None
    rrf_score: float | None = None
    rerank_score: float | None = None

    # Retrieval ranks
    vector_rank: int | None = None
    lexical_rank: int | None = None
    rrf_rank: int | None = None

    # Retrieval channels that contributed
    retrieval_sources: list[str] = field(
        default_factory=list
    )

    # Extra information for future retrieval strategies
    metadata: dict[str, Any] = field(
        default_factory=dict
    )