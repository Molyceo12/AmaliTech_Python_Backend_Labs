"""``POST /api/urls/``: create a short URL."""

from rest_framework import generics

from shortener.serializers import ShortURLSerializer
from shortener.services.short_codes import create_short_url


class ShortURLCreateView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Save a long URL under a new short code."""

    serializer_class = ShortURLSerializer

    def perform_create(self, serializer: ShortURLSerializer) -> None:  # type: ignore[override]
        """Let the service pick the code and save the URL."""
        serializer.instance = create_short_url(
            serializer.validated_data["original_url"]
        )
