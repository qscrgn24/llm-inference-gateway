import logging
from typing import List, Dict, Any

from openai import AsyncOpenAI
from openai import RateLimitError, APITimeoutError, APIConnectionError, APIStatusError

from app.core.config import settings
from app.core.errors import (
    UpstreamTimeout,
    UpstreamRateLimited,
    UpstreamUnavailable,
    BadUpstreamResponse,
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

    async def embed(self, inputs: List[str], model: str) -> Dict[str, Any]:
        try:
            resp = await self.client.embeddings.create(
                model=model,
                input=inputs,
            )
        except APITimeoutError:
            raise UpstreamTimeout()
        except RateLimitError:
            raise UpstreamRateLimited()
        except APIConnectionError:
            raise UpstreamUnavailable("Upstream provider connection error")
        except APIStatusError as e:
            status = getattr(e, "status_code", None)
            if status in (500, 502, 503, 504):
                raise UpstreamUnavailable(f"Upstream provider error (status {status})")
            raise BadUpstreamResponse(f"Upstream provider error (status {status})")
        except Exception:
            logger.exception("Unexpected error calling OpenAI embeddings")
            raise BadUpstreamResponse("Unexpected upstream error")

        try:
            vectors = [d.embedding for d in resp.data]
        except Exception:
            raise BadUpstreamResponse("Malformed upstream response: missing embeddings")

        usage = None
        if resp.usage:
            usage = {"total_tokens": getattr(resp.usage, "total_tokens", None)}

        return {
            "embeddings": vectors,
            "model": model,
            "usage": usage,
        }