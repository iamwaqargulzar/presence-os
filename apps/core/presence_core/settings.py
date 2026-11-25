"""Settings come only from the environment; see .env.example at the repository root."""

import os
from typing import Any

SECRET_KEY = os.environ["PRESENCE_SECRET_KEY"]
DEBUG = os.environ.get("PRESENCE_DEBUG") == "1"
ALLOWED_HOSTS = os.environ.get("PRESENCE_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

ROOT_URLCONF = "presence_core.urls"
INSTALLED_APPS = ["django.contrib.contenttypes", "presence_core"]
MIDDLEWARE = [
    "presence_core.observability.RequestIdMiddleware",
    "django.middleware.security.SecurityMiddleware",
]
# shortcut: one role owns and uses the tables, R0-003 splits it into migration and runtime roles.
DATABASES: dict[str, Any] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PRESENCE_DB_NAME", "presence_dev"),
        "USER": os.environ.get("PRESENCE_DB_USER", "presence"),
        "PASSWORD": os.environ.get("PRESENCE_DB_PASSWORD", ""),
        "HOST": os.environ.get("PRESENCE_DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("PRESENCE_DB_PORT", "15432"),
    }
}

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
