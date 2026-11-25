import json
import logging
import re
import time
import uuid
from collections.abc import Callable
from contextvars import ContextVar

from django.http import HttpRequest, HttpResponse

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Incoming IDs are untrusted: accept only short plain tokens so they cannot forge log lines.
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

logger = logging.getLogger("presence.request")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
            **getattr(record, "fields", {}),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        return json.dumps(entry, default=str)


class RequestIdMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if _SAFE_ID.match(incoming) else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        start = time.monotonic()
        try:
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            logger.info(
                "request",
                extra={
                    "fields": {
                        "method": request.method,
                        "path": request.path,
                        "status": response.status_code,
                        "duration_ms": round((time.monotonic() - start) * 1000, 1),
                    }
                },
            )
            return response
        finally:
            request_id_var.reset(token)
