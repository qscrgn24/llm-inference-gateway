import time
from typing import Optional, List

from app.core.logging import request_id_ctx
from app.providers.embeddings_base import EmbeddingsProvider
from app.schemas.embed import EmbeddingsRequest, EmbeddingsResponse, EmbeddingsUsage


class EmbeddingsService:
    """
    Orchestrates embedding requests:
    - normalizes input into a list[str]
    - calls provider
    - measures provider latency (inference latency)
    - returns stable response schema
    """

    def __init__(self, provider: EmbeddingsProvider):
        self.provider = provider

    async def embed(self, request: EmbeddingsRequest) -> EmbeddingsResponse:
        inputs: List[str]
        if isinstance(request.input, str):
            inputs = [request.input]
        else:
            inputs = request.input

        start = time.perf_counter()
        provider_result = await self.provider.embed(self, inputs=inputs, model=request.model)
        latency_ms = (time.perf_counter() - start) * 1000.0

        usage: Optional[EmbeddingsUsage] = None
        raw_usage = provider_result.get("usage")
        if isinstance(raw_usage, dict):
            usage = EmbeddingsUsage(total_tokens=raw_usage.get("total_tokens"))

        request_id = request_id_ctx.get() or "unknown"

        return EmbeddingsResponse(
            embeddings=provider_result.get("embeddings", []),
            model=str(provider_result.get("model", request.model)),
            latency_ms=round(latency_ms, 2),
            request_id=request_id,
            usage=usage,
        )