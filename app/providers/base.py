from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, List

from app.schemas.chat import ChatMessage


class ChatProvider(ABC):
    """
    Abstract base class for LLM providers.

    Why this exists:
    - Enables swapping OpenAI ↔ HuggingFace ↔ Anthropic
    - Makes service layer independent from vendor SDK
    - Makes unit testing trivial via fake provider
    - Clean separation of concerns (service != vendor client)
    """

    @abstractmethod
    async def generate(self, messages: List[ChatMessage], model: str, temperature: float, max_output_tokens: int) -> dict:
        """
        Should return a dict with at minimum:
        {
            "text": str,
            "model": str,
            "usage": {
                "input_tokens": int | None,
                "output_tokens": int | None,
                "total_tokens": int | None,
            } | None
        }
        """
        raise NotImplementedError
    