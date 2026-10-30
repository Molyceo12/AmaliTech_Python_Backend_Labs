"""``POST /api/urls/``: create a short URL."""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from shortener.serializers import ShortURLCreatedSerializer, ShortURLSerializer
from shortener.services.short_codes import create_short_url
from url_shortener.exceptions import ErrorSerializer


class ShortURLCreateView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Save a long URL under a new short code."""

    serializer_class = ShortURLSerializer

    @extend_schema(responses={201: ShortURLCreatedSerializer, 400: ErrorSerializer})
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return the new short URL with ``status_code`` first, like errors do."""
        response = super().post(request, *args, **kwargs)
        response.data = {"status_code": response.status_code, **response.data}
        return response

    def perform_create(self, serializer: ShortURLSerializer) -> None:  # type: ignore[override]
        """Let the service pick the code and save the URL."""
        serializer.instance = create_short_url(
            serializer.validated_data["original_url"]
        )
