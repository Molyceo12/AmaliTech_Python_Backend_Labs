"""``/api/v1/urls/``: list your URLs (GET) or create one (POST)."""

from django.db.models import QuerySet
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics

from shortener.filters.short_url import ORDERINGS, STATUS_QUERIES, apply_filters
from shortener.models import ShortURL
from shortener.serializers import ShortURLCreatedSerializer, ShortURLSerializer
from shortener.services.short_codes import create_short_url
from url_shortener.exceptions import ERRORS, ErrorSerializer


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter("status", enum=list(STATUS_QUERIES)),
            OpenApiParameter("ordering", enum=ORDERINGS),
            OpenApiParameter("tag", description="Only URLs with this tag."),
        ],
        responses={200: ShortURLSerializer(many=True), **ERRORS},
    ),
    post=extend_schema(
        responses={
            201: ShortURLCreatedSerializer,
            403: ErrorSerializer,
            409: ErrorSerializer,
            **ERRORS,
        }
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
