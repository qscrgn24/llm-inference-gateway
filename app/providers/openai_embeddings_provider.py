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
from app.providers.embeddings_base import EmbeddingsProvider

logger = logging.getLogger(__name__)


class OpenAIEmbeddingsProvider(EmbeddingsProvider):
    def __init__(self) -> None:
        if not settings.openai_api_key:
            logger.warning("OPENAI_API_KEY is not set; OpenAIEmbeddingsProvider will fail if called.")

        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout_s,
            max_retries=settings.openai_max_retries,
        )

    async def embed(self, inputs: list[str], model: str) -> dict[str, Any]:
        try:
            resp = await self.client.embeddings.create(
                model=model,
                input=inputs,
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
            logger.exception("Unexpected error calling OpenAI embeddings")
            raise BadUpstreamResponse("Unexpected upstream error") from e

        try:
            vectors = [d.embedding for d in resp.data]
        except Exception as e:
            raise BadUpstreamResponse("Malformed upstream response: missing embeddings") from e

        usage = None
        if resp.usage:
            usage = {"total_tokens": getattr(resp.usage, "total_tokens", None)}

        return {
            "embeddings": vectors,
            "model": model,
            "usage": usage,
        }