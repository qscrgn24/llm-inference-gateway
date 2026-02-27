import json
import logging
import os
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

# Request-scoped context (set by middleware)
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    """
    Minimal JSON log formatter.

    Why JSON logs?
    - Machine-parseable (CloudWatch, ELK, Datadog)
    - Enables filtering by request_id, level, path, etc.
    - Avoids brittle string parsing
    """

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        rid = request_id_ctx.get()
        if rid:
            payload["request_id"] = rid

        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            payload.update(fields)

        return json.dumps(payload, ensure_ascii=False)
    

def setup_logging() -> None:
    """
    Configure root logging once at app startup.

    Interview-ready points:
    - Centralized logging config (no ad-hoc print statements)
    - JSON logs for production observability
    - Log level controlled via environment variable (12-factor)
    """

    level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_str, logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)