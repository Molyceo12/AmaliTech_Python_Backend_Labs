"""``POST /api/v1/urls/``: create a short URL."""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics

from shortener.serializers import ShortURLCreatedSerializer, ShortURLSerializer
from shortener.services.short_codes import create_short_url
from url_shortener.exceptions import ErrorSerializer


@extend_schema_view(
    post=extend_schema(
        responses={
            201: ShortURLCreatedSerializer,
            400: ErrorSerializer,
            500: ErrorSerializer,
        }
    )
)
class ShortURLCreateView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Save a long URL under a new short code (the renderer wraps the body)."""

    serializer_class = ShortURLSerializer

    def perform_create(self, serializer: ShortURLSerializer) -> None:  # type: ignore[override]
        """Let the service pick the code and save the URL."""
        serializer.instance = create_short_url(
            serializer.validated_data["original_url"]
        )
