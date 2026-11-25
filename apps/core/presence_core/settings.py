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
# Two roles (R0-003, docs/security/database-tenancy-rls.md): the runtime role serves requests under
# row-level security and owns nothing; the migration role owns the schema and only runs migrations.
_DB = {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": os.environ.get("PRESENCE_DB_NAME", "presence_dev"),
    "HOST": os.environ.get("PRESENCE_DB_HOST", "127.0.0.1"),
    "PORT": os.environ.get("PRESENCE_DB_PORT", "15432"),
}
DATABASES: dict[str, Any] = {
    "default": {
        **_DB,
        "USER": "presence_app",
        "PASSWORD": os.environ.get("PRESENCE_DB_APP_PASSWORD", ""),
        # Reused connections are safe because the tenant setting is transaction-scoped.
        "CONN_MAX_AGE": 60,
        "CONN_HEALTH_CHECKS": True,
        # Tests reuse the migration role's test database but still connect as presence_app.
        "TEST": {"MIRROR": "migrator"},
    },
    "migrator": {
        **_DB,
        "USER": "presence_migrator",
        "PASSWORD": os.environ.get("PRESENCE_DB_MIGRATOR_PASSWORD", ""),
    },
}
DATABASE_ROUTERS = ["presence_core.tenancy.MigrateWithMigratorOnly"]

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
