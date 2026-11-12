"""``/api/v1/urls/<short_code>/``: show, change or delete one URL."""

from typing import Any

from django.db.models import Count
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from shortener.models import ShortURL
from shortener.permissions import IsOwnerOrReadOnly
from shortener.serializers import ShortURLDetailSerializer
from shortener.views.lookup import get_by_code_or_alias
from url_shortener.exceptions import ERRORS, ErrorSerializer

DETAIL_ERRORS = {**ERRORS, 404: ErrorSerializer}
CHANGE_ERRORS = {**DETAIL_ERRORS, 403: ErrorSerializer, 409: ErrorSerializer}


@extend_schema_view(
    get=extend_schema(responses={200: ShortURLDetailSerializer, **DETAIL_ERRORS}),
    put=extend_schema(responses={200: ShortURLDetailSerializer, **CHANGE_ERRORS}),
    patch=extend_schema(responses={200: ShortURLDetailSerializer, **CHANGE_ERRORS}),
    delete=extend_schema(
        responses={
            200: OpenApiResponse(description="Short URL deleted; detail is null."),
            401: ErrorSerializer,
            403: ErrorSerializer,
            404: ErrorSerializer,
        }
    ),
)
class ShortURLDetailView(generics.RetrieveUpdateDestroyAPIView):  # type: ignore[type-arg]
    """Show one short URL (by code or alias); its owner can also change or delete it."""

    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = ShortURLDetailSerializer
    success_messages = {
        "GET": "Short URL loaded.",
        "PUT": "Short URL updated.",
        "PATCH": "Short URL updated.",
        "DELETE": "Short URL deleted.",
    }
    # The database counts the clicks: one query, not one per click.
    queryset = (
        ShortURL.objects.select_related("owner")
        .prefetch_related("tags")
        .annotate(total_clicks=Count("clicks"))
    )

    def get_object(self) -> ShortURL:
        """By short code or alias."""
        return get_by_code_or_alias(self)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete, then answer 200 (not 204) so the client gets a toast message."""
        self.perform_destroy(self.get_object())
        return Response(None)
