"""Structured logs, correlation IDs and redaction (R0-001, R0-006; docs/infrastructure/observability.md)."""

import json
import logging
import re
import secrets
import time
import uuid
from collections.abc import Callable, Iterator, Mapping
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from django.http import HttpRequest, HttpResponse

# Correlation IDs of the current request or job: request, trace, tenant, profile, workflow, task, action.
CORRELATION_KEYS = ("request_id", "trace_id", "tenant_id", "profile_id", "workflow_id", "task_id", "action_id")
_correlation: ContextVar[Mapping[str, str]] = ContextVar("correlation", default={})  # noqa: B039 (never mutated)

# Incoming IDs are untrusted: accept only short plain tokens so they cannot forge log lines.
_SAFE_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
# W3C Trace Context, the OpenTelemetry default propagator: version-traceid-parentid-flags.
_TRACEPARENT = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-[0-9a-f]{2}$")

logger = logging.getLogger("presence.request")


@contextmanager
def correlate(**ids: object) -> Iterator[None]:
    """Add correlation IDs (keys from CORRELATION_KEYS) to every log line and audit event in the block."""
    unknown = ids.keys() - set(CORRELATION_KEYS)
    if unknown:
        raise ValueError(f"unknown correlation keys: {sorted(unknown)}")
    token = _correlation.set({**_correlation.get(), **{k: str(v) for k, v in ids.items() if v is not None}})
    try:
        yield
    finally:
        _correlation.reset(token)


def correlation() -> Mapping[str, str]:
    return _correlation.get()


# --- Redaction (E-036): applied to every log line and every audit payload before it is written. ---

REDACTED = "[REDACTED]"
# Keys whose values are never kept, whatever they contain.
_SENSITIVE_KEY = re.compile(
    r"pass(word|wd|phrase)?|secret|token|authorization|cookie|api[-_]?key|credential|private[-_]?key|session|otp",
    re.IGNORECASE,
)
# Values that look like credentials or personal data, wherever they appear in text.
_SENSITIVE_TEXT = re.compile(
    r"(?i:bearer|basic)\s+[A-Za-z0-9._~+/=-]{8,}"  # Authorization header values
    r"|eyJ[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]{5,}\.[A-Za-z0-9_-]*"  # JWT
    r"|\b(?:sk|pk|rk)-[A-Za-z0-9_-]{16,}"  # provider API keys (sk-..., sk-ant-...)
    r"|\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})"  # GitHub tokens
    r"|\bxox[abprs]-[A-Za-z0-9-]{10,}"  # Slack tokens
    r"|\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"  # AWS access key IDs
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----"
    r"|(?i:pass(?:word|wd)?|secret|token|api[-_]?key|session(?:id)?)\s*[=:]\s*[^\s&;,]+"  # key=value pairs
    r"|(?i:cookie):\s*[^\r\n]+"  # Cookie / Set-Cookie header lines
    r"|(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+"  # email addresses (personal data)
)


def redact(value: Any) -> tuple[Any, int]:
    """Return a copy of `value` (str, dict, list, tuple or scalar) with secrets replaced, and the hit count."""
    if isinstance(value, str):
        return _SENSITIVE_TEXT.subn(REDACTED, value)
    if isinstance(value, Mapping):
        out: dict[str, Any] = {}
        hits = 0
        for key, item in value.items():
            if isinstance(key, str) and _SENSITIVE_KEY.search(key) and item not in (None, ""):
                out[key], hits = REDACTED, hits + 1
            else:
                out[str(key)], n = redact(item)
                hits += n
        return out, hits
    if isinstance(value, list | tuple):
        pairs = [redact(item) for item in value]
        return [item for item, _ in pairs], sum(n for _, n in pairs)
    return value, 0


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            "request_id": None,
            **correlation(),
            **getattr(record, "fields", {}),
        }
        if record.exc_info:
            entry["exc"] = self.formatException(record.exc_info)
        entry, hits = redact(entry)
        if hits:
            entry["redactions"] = hits  # health signal: how often something sensitive reached a log call
        return json.dumps(entry, default=str)


def _trace_id(traceparent: str) -> str:
    match = _TRACEPARENT.match(traceparent)
    if match and match[1] != "0" * 32 and match[2] != "0" * 16:
        return match[1]
    return secrets.token_hex(16)


class RequestIdMiddleware:
    """Sets request and trace IDs for the request; continues an incoming W3C trace when the header is valid."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        incoming = request.headers.get("X-Request-ID", "")
        request_id = incoming if _SAFE_ID.match(incoming) else uuid.uuid4().hex
        trace_id = _trace_id(request.headers.get("traceparent", ""))
        start = time.monotonic()
        with correlate(request_id=request_id, trace_id=trace_id):
            response = self.get_response(request)
            response["X-Request-ID"] = request_id
            # shortcut: no span export yet; the response names this hop so callers can join traces.
            response["traceparent"] = f"00-{trace_id}-{secrets.token_hex(8)}-01"
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
