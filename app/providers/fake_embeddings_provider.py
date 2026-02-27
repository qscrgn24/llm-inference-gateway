from __future__ import annotations

from typing import List

from app.providers.embeddings_base import EmbeddingsProvider


class FakeEmbeddingsProvider(EmbeddingsProvider):
    """
    Deterministic fake embeddings provider for tests.

    Returns a fixed-size vector per input (no external calls).
    """

    async def embed(self, inputs: List[str], model: str) -> dict:
        embeddings: List[List[float]] = []
        for s in inputs:
            n = float(len(s))
            embeddings.append([n, n + 1.0, n + 2.0, n + 3.0])

        return {
            "embeddings": embeddings,
            "model": model,
            "usage": {"total_tokens": None},
        }