from __future__ import annotations

from typing import List, Union, Optional

from pydantic import BaseModel, Field, ConfigDict


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

    input: Union[str, List[str]] = Field(...)
    model: str = Field(default="text-embedding-3-small", min_length=1, max_length=100)

    model_config = ConfigDict(extra="forbid")


class EmbeddingsUsage(BaseModel):
    total_tokens: Optional[int] = None
    model_config = ConfigDict(extra="forbid")


class EmbeddingsResponse(BaseModel):
    embeddings: List[List[float]]
    model: str
    latency_ms: float
    request_id: str
    usage: Optional[EmbeddingsUsage] = None

    model_config = ConfigDict(extra="forbid")