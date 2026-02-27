import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI

from app.core.config import settings
from app.providers.base import ChatProvider
from app.schemas.chat import ChatMessage

logger = logging.getLogger(__name__)


class OpenAIChatProvider(ChatProvider):
    """
    OpenAI implementation of ChatProvider.

    Design goals (production signal):
    - single client reused (connection pooling via httpx under the hood)
    - timeout + retries configured via env (12-factor)
    - returns a stable dict shape consumed by ChatService
    """

    def __init__(self) -> None:
        if not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY is not set; OpenAIChatProvider will fail if called.")

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_s,
            max_retries=settings.openai_max_retries,
        )

    async def generate(self, messages: List[ChatMessage], model: str, temperature: float, max_output_tokens: int) -> Dict[str, Any]:
        # Convert Pydantic models -> OpenAI message dicts
        oai_messages = [{"role": m.role, "content": m.content} for m in messages]

        # Chat Completions API (supported long-term by OpenAI Python SDK)
        resp = await self.client.chat.completions.create(
            model=model,
            messages=oai_messages,
            temperature=temperature,
            max_tokens=max_output_tokens,
        )

        text = resp.choices[0].message.content or ""

        usage = None
        if resp.usage:
            usage = {
                "input_tokens": getattr(resp.usage, "prompt_tokens", None),
                "output_tokens": getattr(resp.usage, "completion_tokens", None),
                "total_tokens": getattr(resp.usage, "total_tokens", None),
            }

        return {
            "text": text,
            "model": model,
            "usage": usage,
        }