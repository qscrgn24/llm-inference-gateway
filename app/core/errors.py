from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AppError(Exception):
    """
    Base application error with an HTTP-safe shape.

    Why this exists:
    - keeps error responses consistent
    - prevents leaking vendor/internal details
    - makes error handling testable
    """
    status_code: int
    code: str
    message: str
    retryable: bool = False
    details: dict | None = None


class UpstreamTimeout(AppError):
    def __init__(self, message: str = "Upstream provider timed out"):
        super().__init__(status_code=504, code="UPSTREAM_TIMEOUT", message=message, retryable=True)


class UpstreamRateLimited(AppError):
    def __init__(self, message: str = "Upstream provider rate limited the request"):
        super().__init__(status_code=429, code="UPSTREAM_RATE_LIMITED", message=message, retryable=True)


class UpstreamUnavailable(AppError):
    def __init__(self, message: str = "Upstream provider unavailable"):
        super().__init__(status_code=503, code="UPSTREAM_UNAVAILABLE", message=message, retryable=True)


class BadUpstreamResponse(AppError):
    def __init__(self, message: str = "Upstream provider returned an invalid response"):
        super().__init__(status_code=502, code="BAD_UPSTREAM_RESPONSE", message=message, retryable=True)