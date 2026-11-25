"""Settings come only from the environment; see .env.example at the repository root."""

import os
from typing import Any

SECRET_KEY = os.environ["PRESENCE_SECRET_KEY"]
DEBUG = os.environ.get("PRESENCE_DEBUG") == "1"
ALLOWED_HOSTS = os.environ.get("PRESENCE_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

ROOT_URLCONF = "presence_core.urls"
INSTALLED_APPS: list[str] = []
MIDDLEWARE = [
    "presence_core.observability.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
]
# No database until R0-003, which adds PostgreSQL with a runtime role that does not own tables.
DATABASES: dict[str, Any] = {}

USE_TZ = True
TIME_ZONE = "UTC"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "presence_core.observability.JsonFormatter"}},
    "handlers": {"stdout": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["stdout"], "level": os.environ.get("PRESENCE_LOG_LEVEL", "INFO")},
    # presence.request already logs every request with its ID; keep only django.server errors.
    "loggers": {"django.server": {"handlers": ["stdout"], "level": "WARNING", "propagate": False}},
}
