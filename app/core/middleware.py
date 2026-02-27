import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

from app.core.logging import request_id_ctx

logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Adds production-grade request context:
    - request_id: taken from X-Request-ID if provided, else generated
    - latency_ms: measured end-to-end at the middleware level
    - sets response headers: X-Request-ID, X-Response-Time-ms
    """
    def __init__(self, app: ASGIApp, request_id_header: str = "X-Request-ID", response_time_header: str = "X-Response-Time-ms") -> None:
        super().__init__(app)
        self.request_id_header = request_id_header
        self.response_time_header = response_time_header

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        start = time.perf_counter()

        # 1) Request ID: accept upstream ID or generate a new one
        incoming_rid: str | None = request.headers.get(self.request_id_header)
        rid = incoming_rid.strip() if incoming_rid else str(uuid.uuid4())

        # Store request_id in context var for log enrichment
        token = request_id_ctx.set(rid)

        try:
            response = await call_next(request)
        except Exception:
            # Log exception with request_id already attached via ContextVar
            logger.exception("Unhandled exception while processing request", extra={"fields": {"method": request.method, "path": request.url.path}})
            raise
        finally:
            # Reset context var to avoid leaking across requests
            request_id_ctx.reset(token)

        # 2) Latency
        latency_ms = (time.perf_counter() - start) * 1000.0

        # Add headers for debugging / client visibility
        response.headers[self.request_id_header] = rid
        response.headers[self.response_time_header] = f"{latency_ms:.2f}"

        # Structured access log
        logger.info("request completed", extra={"fields": {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": round(latency_ms, 2),
        }})

        return response