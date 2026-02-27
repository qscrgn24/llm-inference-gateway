import time

from app.core.logging import request_id_ctx
from app.providers.base import ChatProvider
from app.schemas.chat import ChatRequest, ChatResponse, ChatUsage


class ChatService:
    """
    Orchestrates chat requests.

    Responsibilities:
    - call provider
    - measure provider latency (inference latency)
    - shape provider output into a stable API response
    """

    def __init__(self, provider: ChatProvider):
        self.provider = provider

    async def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()

        provider_result = await self.provider.generate(
            messages = request.messages,
            model = request.model,
            temperature= request.temperature,
            max_output_tokens= request.max_output_tokens,
        )

        latency_ms = (time.perf_counter() - start) * 1000.0

        usage: ChatUsage | None = None,
        raw_usage = provider_result.get("usage")
        if isinstance(raw_usage, dict):
            usage = ChatUsage(
                input_tokens=raw_usage.get("input_tokens"),
                output_tokens=raw_usage.get("output_tokens"),
                total_tokens=raw_usage.get("total_tokens"),
            )

        request_id = request_id_ctx.get() or "unknown"

        return ChatResponse(
            text=str(provider_result.get("text", "")),
            model=str(provider_result.get("model", request.model)),
            latency_ms=round(latency_ms, 2),
            request_id=request_id,
            usage=usage,
        )