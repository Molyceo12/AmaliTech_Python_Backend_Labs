"""``/api/v1/urls/``: list and create; ``/api/v1/urls/<short_code>/``: one URL."""

from typing import Any

from django.db.models import Count, QuerySet
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
)
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from shortener.filters.short_url import ORDERINGS, STATUS_QUERIES, apply_filters
from shortener.models import ShortURL
from shortener.serializers import (
    ShortURLCreatedSerializer,
    ShortURLDetailSerializer,
    ShortURLSerializer,
)
from shortener.services.short_codes import create_short_url
from url_shortener.exceptions import ErrorSerializer

ERRORS = {400: ErrorSerializer, 401: ErrorSerializer, 500: ErrorSerializer}
DETAIL_ERRORS = {**ERRORS, 404: ErrorSerializer}


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter("status", enum=list(STATUS_QUERIES)),
            OpenApiParameter("ordering", enum=ORDERINGS),
        ],
        responses={200: ShortURLSerializer(many=True), **ERRORS},
    ),
    post=extend_schema(
        responses={201: ShortURLCreatedSerializer, 409: ErrorSerializer, **ERRORS}
    ),
)
class ShortURLListCreateView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """List your own short URLs (20 per page), or save a long URL under a new code."""

    serializer_class = ShortURLSerializer
    success_messages = {"GET": "Short URLs loaded.", "POST": "Short URL created."}

    def get_queryset(self) -> QuerySet[ShortURL]:
        """Only the user's URLs: one query for URLs + owners, one for tags (no N+1)."""
        queryset = (
            ShortURL.objects.filter(owner_id=self.request.user.pk)
            .select_related("owner")
            .prefetch_related("tags")
        )
        return apply_filters(queryset, self.request.query_params)

    def perform_create(self, serializer: ShortURLSerializer) -> None:  # type: ignore[override]
        """Let the service pick the code and save the URL and its tags."""
        serializer.instance = create_short_url(
            owner=self.request.user, **serializer.validated_data
        )


@extend_schema_view(
    get=extend_schema(responses={200: ShortURLDetailSerializer, **DETAIL_ERRORS}),
    put=extend_schema(
        responses={200: ShortURLDetailSerializer, 409: ErrorSerializer, **DETAIL_ERRORS}
    ),
    patch=extend_schema(
        responses={200: ShortURLDetailSerializer, 409: ErrorSerializer, **DETAIL_ERRORS}
    ),
    delete=extend_schema(
        responses={
            200: OpenApiResponse(description="Short URL deleted; detail is null."),
            401: ErrorSerializer,
            404: ErrorSerializer,
        }
    ),
)
class ShortURLDetailView(generics.RetrieveUpdateDestroyAPIView):  # type: ignore[type-arg]
    """Show, change or delete one short URL, found by its code."""

    serializer_class = ShortURLDetailSerializer
    success_messages = {
        "GET": "Short URL loaded.",
        "PUT": "Short URL updated.",
        "PATCH": "Short URL updated.",
        "DELETE": "Short URL deleted.",
    }
    lookup_field = "short_code"
    # The database counts the clicks: one query, not one per click.
    queryset = (
        ShortURL.objects.select_related("owner")
        .prefetch_related("tags")
        .annotate(total_clicks=Count("clicks"))
    )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Delete, then answer 200 (not 204) so the client gets a toast message."""
        self.perform_destroy(self.get_object())
        return Response(None)
