"""One JSON shape for every API error: ``{"status_code": ..., "detail": ...}``."""

from typing import Any

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import exception_handler


def json_exception_handler(exc: Exception, context: dict[str, Any]) -> Response | None:
    """Wrap DRF's error body with its status code.

    Field errors stay a dict under ``detail``, e.g.
    ``{"status_code": 400, "detail": {"original_url": ["Enter a valid URL."]}}``.
    """
    response = exception_handler(exc, context)
    if response is not None:
        data = response.data
        detail = data["detail"] if isinstance(data, dict) and "detail" in data else data
        response.data = {"status_code": response.status_code, "detail": detail}
    return response


# Only describes the error body for Swagger; it never saves anything.
class ErrorSerializer(serializers.Serializer[Any]):  # pylint: disable=abstract-method
    """Shape of every error, for the Swagger docs."""

    status_code = serializers.IntegerField()
    detail = serializers.JSONField()
