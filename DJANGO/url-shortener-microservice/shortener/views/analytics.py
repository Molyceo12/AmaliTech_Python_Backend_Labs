"""``/api/v1/analytics/<short_code>/``: detailed clicks for Premium owners."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from shortener.models import ShortURL
from shortener.permissions import IsOwner, IsPremium
from shortener.serializers import AnalyticsSerializer
from shortener.services.analytics import UrlAnalytics, url_analytics
from shortener.views.lookup import get_by_code_or_alias
from url_shortener.exceptions import ErrorSerializer


@extend_schema(
    responses={
        200: AnalyticsSerializer,
        **dict.fromkeys([401, 403, 404, 500], ErrorSerializer),
    }
)
class AnalyticsView(generics.RetrieveAPIView):  # type: ignore[type-arg]
    """Clicks per day and per country of one of your URLs, by code or alias."""

    permission_classes = [IsAuthenticated, IsPremium, IsOwner]
    serializer_class = AnalyticsSerializer
    queryset = ShortURL.objects.all()
    success_messages = {"GET": "Analytics loaded."}

    def get_object(self) -> UrlAnalytics:
        """The numbers of the URL found by short code or alias (owner checked)."""
        return url_analytics(get_by_code_or_alias(self))
