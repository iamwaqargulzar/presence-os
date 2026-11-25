from django.http import HttpRequest, JsonResponse
from django.urls import path
from django.views.decorators.http import require_safe


@require_safe
def healthz(request: HttpRequest) -> JsonResponse:
    # Unauthenticated: must never return tenant, build or secret data.
    return JsonResponse({"status": "ok"})


urlpatterns = [path("healthz", healthz)]
