"""``/api/urls/``: list and create; ``/api/urls/<short_code>/``: one URL."""

from typing import Any

from django.db.models import Count, QuerySet
from drf_spectacular.utils import (
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response

from shortener.models import ShortURL
from shortener.serializers import (
    ShortURLCreatedSerializer,
    ShortURLDetailSerializer,
    ShortURLSerializer,
)
from shortener.services.short_codes import create_short_url
from url_shortener.exceptions import ErrorSerializer

# ?status= picks one of the custom queries from branch 6.
STATUS_QUERIES = {"active": "active_urls", "expired": "expired_urls"}

ERRORS = {400: ErrorSerializer, 500: ErrorSerializer}
DETAIL_ERRORS = {**ERRORS, 404: ErrorSerializer}


def _filtered(queryset: Any, params: Any) -> QuerySet[ShortURL]:
    """Apply ``?status=active|expired`` and ``?ordering=popular``; else 400."""
    status = params.get("status")
    if status is not None:
        if status not in STATUS_QUERIES:
            raise ValidationError({"status": ["Use active or expired."]})
        queryset = getattr(queryset, STATUS_QUERIES[status])()
    ordering = params.get("ordering")
    if ordering is not None:
        if ordering != "popular":
            raise ValidationError({"ordering": ["Use popular."]})
        queryset = queryset.popular_urls()
    return queryset  # type: ignore[no-any-return]


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter("status", enum=list(STATUS_QUERIES)),
            OpenApiParameter("ordering", enum=["popular"]),
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
        return _filtered(queryset, self.request.query_params)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Wrap the new short URL as ``{status_code, message, detail}``."""
        response = super().post(request, *args, **kwargs)
        response.data = {
            "status_code": response.status_code,
            "message": "Short URL created.",
            "detail": response.data,
        }
        return response

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
