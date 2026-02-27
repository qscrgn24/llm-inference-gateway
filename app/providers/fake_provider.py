from __future__ import annotations

from typing import List

from app.providers.base import ChatProvider
from app.schemas.chat import ChatMessage


class FakeChatProvider(ChatProvider):
    """
    Deterministic provider used for tests and local scaffolding.

    Why:
    - keeps tests offline and fast
    - avoids API key dependency in CI
    - allows strict TDD flow before integrating a real vendor SDK
    """

    async def generate(self, messages: List[ChatMessage], model: str, temperature:float, max_output_tokens: int) -> dict:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        text = f"echo: {last_user}" if last_user else "echo:"

        return {
            "text": text,
            "model": model,
            "usage": {
                "input_tokens": None,
                "output_tokens": None,
                "total_tokens": None,
            }
        }