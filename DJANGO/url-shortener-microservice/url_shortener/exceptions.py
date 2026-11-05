"""One JSON shape for every error: ``{"status_code": ..., "detail": ...}``."""

import logging
from typing import Any

from django.http import HttpRequest, JsonResponse
from rest_framework import serializers, status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)

SERVER_ERROR = {"status_code": 500, "detail": "Internal server error."}


class Conflict(APIException):
    """409: the value is already used, e.g. a taken custom alias."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "Conflict."


class Gone(APIException):
    """410: the resource existed but is no longer available, e.g. expired."""

    status_code = status.HTTP_410_GONE
    default_detail = "Gone."


def json_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    """Wrap DRF's error body with its status code.

    Field errors stay a dict under ``detail``, e.g.
    ``{"status_code": 400, "detail": {"original_url": ["Enter a valid URL."]}}``.
    Any other error (a bug, the database down) is logged and becomes a JSON 500.
    """
    response = exception_handler(exc, context)
    if response is None:
        logger.error("Unhandled error in %s", context.get("view"), exc_info=exc)
        return Response(SERVER_ERROR, status=500)
    data = response.data
    detail = data["detail"] if isinstance(data, dict) and "detail" in data else data
    response.data = {"status_code": response.status_code, "detail": detail}
    return response


# Django passes ``exception`` by name, so it keeps this name though unused.
def not_found(
    request: HttpRequest, exception: Exception  # pylint: disable=unused-argument
) -> JsonResponse:
    """``handler404``: JSON for a route that does not exist (e.g. ``/a/b/``)."""
    return JsonResponse({"status_code": 404, "detail": "Not found."}, status=404)


def server_error(request: HttpRequest) -> JsonResponse:
    """``handler500``: JSON for a crash outside an API view (Django logs it)."""
    return JsonResponse(SERVER_ERROR, status=500)


# Only describes the error body for Swagger; it never saves anything.
class ErrorSerializer(serializers.Serializer[Any]):  # pylint: disable=abstract-method
    """Shape of every error, for the Swagger docs."""

    status_code = serializers.IntegerField()
    detail = serializers.JSONField()
