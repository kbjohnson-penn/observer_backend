"""
Embedding client stub — implemented in Phase 6 (MedCPT query encoder).
"""


class EmbeddingClient:
    """Encodes a query string into a dense vector for kNN search."""

    def encode(self, text: str) -> list[float]:
        raise NotImplementedError(
            "EmbeddingClient is not implemented yet. "
            "It will be added in Phase 6 using MedCPT query encoder."
        )
