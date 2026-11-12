"""One short URL with its click totals."""

from typing import Any

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from shortener.models import ShortURL
from shortener.serializers.schema import CountryClicksSerializer
from shortener.serializers.short_url import ShortURLSerializer
from shortener.services.limits import has_paid_tier


class ShortURLDetailSerializer(ShortURLSerializer):
    """One URL, plus click totals counted by the database (``annotate``)."""

    total_clicks = serializers.IntegerField(read_only=True)
    clicks_by_country = serializers.SerializerMethodField()

    class Meta(ShortURLSerializer.Meta):
        """Same fields plus the click totals."""

        fields = [*ShortURLSerializer.Meta.fields, "total_clicks", "clicks_by_country"]

    def get_fields(self) -> dict[str, Any]:
        """Country stats are geo analytics: only paid tiers get them."""
        fields: dict[str, Any] = super().get_fields()
        request = self.context.get("request")
        if request is not None and not has_paid_tier(request.user):
            fields.pop("clicks_by_country")
        return fields

    @extend_schema_field(CountryClicksSerializer(many=True))
    def get_clicks_by_country(self, url: ShortURL) -> list[dict[str, Any]]:
        """``[{"country": "Rwanda", "total": 3}, ...]``, most clicks first."""
        return url.clicks_by_country()
