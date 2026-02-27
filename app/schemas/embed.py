from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class EmbeddingsRequest(BaseModel):
    """
    Request contract for POST /v1/embeddings

    Supports:
    - single string
    - batch of strings

    Production notes:
    - bounds protect latency/cost
    - extra fields forbidden to avoid silent bugs
    """

    input: str | list[str] = Field(...)
    model: str = Field(default="text-embedding-3-small", min_length=1, max_length=100)

    model_config = ConfigDict(extra="forbid")


class EmbeddingsUsage(BaseModel):
    total_tokens: int | None = None
    model_config = ConfigDict(extra="forbid")


class EmbeddingsResponse(BaseModel):
    embeddings: list[list[float]]
    model: str
    latency_ms: float
    request_id: str
    usage: EmbeddingsUsage | None = None

    model_config = ConfigDict(extra="forbid")