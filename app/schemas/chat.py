from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["system", "user", "assistant"]

class ChatMessage(BaseModel):
    """
    A single chat message.

    Production note:
    - Constraining `role` prevents invalid inputs early (422 instead of silent bugs).
    """

    role: Role
    content: str = Field(min_length=1, max_length=20_000)


class ChatRequest(BaseModel):
    """
    Request contract for POST /v1/chat

    Intentionally minimal but realistic:
    - model: lets caller select a model (or you can enforce defaults in config later)
    - temperature: controllable randomness
    - max_output_tokens: prevents runaway cost/latency
    """
    messages: list[ChatMessage] = Field(min_length=1, max_length=50)
    model: str = Field(default="gpt-o-mini", min_length=1, max_length=200)
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_output_tokens: int = Field(default=256, ge=1, le=4096)

    client_request_id: str | None = Field(default=None, max_length=200)

    model_config = ConfigDict(extra="forbid")


class ChatUsage(BaseModel):
    """
    Usage is useful signal for AI-backend roles:
    - shows you understand cost/accounting patterns
    - maps well to OpenAI response usage fields
    """
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None

    model_config = ConfigDict(extra="forbid")


class ChatResponse(BaseModel):
    text: str
    model: str

    latency_ms: float
    request_id: str

    usage: ChatUsage | None = None

    model_config = ConfigDict(extra="forbid")