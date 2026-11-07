"""Errors in the shared shape: ``{"status_code", "message", "detail"}``.

DRF errors are wrapped by ``EnvelopeJSONRenderer``; Django's own error pages
(outside DRF) use the same ``envelope`` here.
"""

import logging
from typing import Any

from django.http import HttpRequest, JsonResponse
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler

from url_shortener.renderers import envelope

logger = logging.getLogger(__name__)

SERVER_ERROR = "Internal server error."


def json_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Keep only DRF's error ``detail``; the renderer adds the rest.

    Field errors stay a dict, e.g. ``{"original_url": ["Enter a valid URL."]}``.
    Any other error (a bug, the database down) is logged and becomes a 500.
    """
    response = exception_handler(exc, context)
    if response is None:
        logger.error("Unhandled error in %s", context.get("view"), exc_info=exc)
        return Response(SERVER_ERROR, status=500)
    data = response.data
    if isinstance(data, dict) and "detail" in data:
        response.data = data["detail"]
    return response


def _json_error(status_code: int, detail: str) -> JsonResponse:
    """A Django error page as JSON in the shared shape."""
    return JsonResponse(envelope(status_code, detail), status=status_code)


# Django passes ``exception`` by name, so the handlers keep it though unused.
def bad_request(
    request: HttpRequest, exception: Exception  # pylint: disable=unused-argument
) -> JsonResponse:
    """``handler400``: e.g. a host not in ``ALLOWED_HOSTS``."""
    return _json_error(400, "Bad request.")


def permission_denied(
    request: HttpRequest, exception: Exception  # pylint: disable=unused-argument
) -> JsonResponse:
    """``handler403``: e.g. a failed CSRF check outside the API."""
    return _json_error(403, "Permission denied.")


def not_found(
    request: HttpRequest, exception: Exception  # pylint: disable=unused-argument
) -> JsonResponse:
    """``handler404``: a route that does not exist (e.g. ``/a/b/``)."""
    return _json_error(404, "Not found.")


def server_error(request: HttpRequest) -> JsonResponse:
    """``handler500``: a crash outside an API view (Django logs it)."""
    return _json_error(500, SERVER_ERROR)


# Only describes the error body for Swagger; it never saves anything.
class ErrorSerializer(serializers.Serializer[Any]):  # pylint: disable=abstract-method
    """Shape of every error, for the Swagger docs."""

    status_code = serializers.IntegerField()
    message = serializers.CharField()
    detail = serializers.JSONField()
