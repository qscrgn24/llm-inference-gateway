import logging
from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.core.config import settings
from app.core.errors import (
    BadUpstreamResponse,
    UpstreamRateLimited,
    UpstreamTimeout,
    UpstreamUnavailable,
)
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

    async def generate(self, messages: list[ChatMessage], model: str, temperature: float, max_output_tokens: int) -> dict[str, Any]:
        # Convert Pydantic models -> OpenAI message dicts
        oai_messages: list[dict[str, Any]] = [{"role": m.role, "content": m.content} for m in messages]

        # Chat Completions API (supported long-term by OpenAI Python SDK)
        try:
            resp = await self.client.chat.completions.create(
                model=model,
                messages=oai_messages, # type: ignore[arg-type]
                temperature=temperature,
                max_tokens=max_output_tokens,
            )
        except APITimeoutError as e:
            raise UpstreamTimeout() from e
        except RateLimitError as e:
            raise UpstreamRateLimited() from e
        except APIConnectionError as e:
            raise UpstreamUnavailable("Upstream provider connection error") from e
        except APIStatusError as e:
            status = getattr(e, "status_code", None)
            if status in (500, 502, 503, 504):
                raise UpstreamUnavailable(f"Upstream provider error (status {status})") from e
            raise BadUpstreamResponse(f"Upstream provider error (status {status})") from e
        except Exception as e:
            logger.exception("Unexpected Error Calling OpenAI")
            raise BadUpstreamResponse("Unexpected upstream error") from e

        try:
            text = resp.choices[0].message.content or ""
        except Exception as e:
            raise BadUpstreamResponse("Malformed upstream response: missing text") from e

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