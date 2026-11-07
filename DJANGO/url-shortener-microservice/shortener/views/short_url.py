"""``/api/v1/urls/``: list and create; ``/api/v1/urls/<short_code>/``: one URL."""

from django.db.models import Count, QuerySet
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import generics

from shortener.filters.short_url import ORDERINGS, STATUS_QUERIES, apply_filters
from shortener.models import ShortURL
from shortener.serializers import (
    ShortURLCreatedSerializer,
    ShortURLDetailSerializer,
    ShortURLSerializer,
)
from shortener.services.short_codes import create_short_url
from url_shortener.exceptions import ErrorSerializer

ERRORS = {400: ErrorSerializer, 500: ErrorSerializer}
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
    """List short URLs (20 per page), or save a long URL under a new code."""

    serializer_class = ShortURLSerializer

    def get_queryset(self) -> QuerySet[ShortURL]:
        """One query for URLs + owners, one for all their tags (no N+1)."""
        queryset = ShortURL.objects.select_related("owner").prefetch_related("tags")
        return apply_filters(queryset, self.request.query_params)

    def perform_create(self, serializer: ShortURLSerializer) -> None:  # type: ignore[override]
        """Let the service pick the code and save the URL and its tags."""
        # Module 7: owner=self.request.user once login exists.
        serializer.instance = create_short_url(owner=None, **serializer.validated_data)


@extend_schema_view(
    get=extend_schema(responses={200: ShortURLDetailSerializer, **DETAIL_ERRORS}),
    put=extend_schema(
        responses={200: ShortURLDetailSerializer, 409: ErrorSerializer, **DETAIL_ERRORS}
    ),
    patch=extend_schema(
        responses={200: ShortURLDetailSerializer, 409: ErrorSerializer, **DETAIL_ERRORS}
    ),
    delete=extend_schema(responses={204: None, 404: ErrorSerializer}),
)
class ShortURLDetailView(generics.RetrieveUpdateDestroyAPIView):  # type: ignore[type-arg]
    """Show, change or delete one short URL, found by its code."""

    serializer_class = ShortURLDetailSerializer
    lookup_field = "short_code"
    # The database counts the clicks: one query, not one per click.
    queryset = (
        ShortURL.objects.select_related("owner")
        .prefetch_related("tags")
        .annotate(total_clicks=Count("clicks"))
    )
