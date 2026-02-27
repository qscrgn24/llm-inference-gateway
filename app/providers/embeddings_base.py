from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingsProvider(ABC):
    """
    Abstract embeddings provider.

    Signal:
    - allows OpenAI ↔ other vendors ↔ local models later
    - keeps service layer vendor-agnostic
    """

    @abstractmethod
    async def embed(self, inputs: list[str], model: str) -> dict:
        """
        Must return dict like:
        {
          "embeddings": List[List[float]],
          "model": str,
          "usage": {"total_tokens": int | None} | None
        }
        """
        raise NotImplementedError