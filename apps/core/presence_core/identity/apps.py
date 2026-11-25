from django.apps import AppConfig


class IdentityConfig(AppConfig):
    name = "presence_core.identity"
    label = "presence_identity"
    verbose_name = "Identity"

    def ready(self) -> None:
        from presence_core.identity import signals  # noqa: F401  (connects the login/logout audit receivers)
