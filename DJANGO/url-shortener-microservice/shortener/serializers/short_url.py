"""Validate short URL input and show saved short URLs."""

from datetime import datetime
from typing import Any

from django.db.models import Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from shortener.models import ShortURL
from shortener.services.short_codes import set_tags
from url_shortener.exceptions import Conflict

# Routes that live at the top level, so an alias can't take their place.
RESERVED_ALIASES = {"api", "admin"}


class TagNamesField(serializers.ListField):
    """Tags in and out as names, e.g. ``["docs", "python"]``."""

    child = serializers.CharField(max_length=50)

    def to_representation(self, data: Any) -> list[str]:
        """``data`` is the URL's tags manager; ``all()`` uses the prefetch."""
        return [tag.name for tag in data.all()]


class ShortURLSerializer(serializers.ModelSerializer[ShortURL]):
    """Takes the URL and its details; returns them with the code and link."""

    short_url = serializers.SerializerMethodField()
    custom_alias = serializers.RegexField(
        r"^[A-Za-z0-9-]+$", max_length=50, required=False, allow_null=True
    )
    tags = TagNamesField(required=False)
    # Module 7 sets the owner from the logged-in user; the client never does.
    owner = serializers.EmailField(
        source="owner.email", read_only=True, allow_null=True
    )

    class Meta:
        """The client sends only what it may change."""

        model = ShortURL
        fields = [
            "original_url",
            "short_code",
            "short_url",
            "custom_alias",
            "title",
            "description",
            "expires_at",
            "is_active",
            "tags",
            "owner",
            "click_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["short_code", "click_count", "created_at", "updated_at"]
        # Without a default, a form post with no is_active box would mean False.
        extra_kwargs = {"is_active": {"default": True}}

    def get_short_url(self, obj: ShortURL) -> str:
        """Full link to open, e.g. ``http://localhost:8000/aB3xY9z/``."""
        path = f"/{obj.short_code}/"
        request: Any = self.context.get("request")
        return str(request.build_absolute_uri(path)) if request else path

    def validate_custom_alias(self, value: str | None) -> str | None:
        """Reserved names → 400; used as an alias or short code → 409."""
        if value is None:
            return value
        if value.lower() in RESERVED_ALIASES:
            raise serializers.ValidationError("This alias is reserved.")
        taken = ShortURL.objects.filter(Q(custom_alias=value) | Q(short_code=value))
        if self.instance is not None:
            taken = taken.exclude(pk=self.instance.pk)
        if taken.exists():
            raise Conflict("This alias is already taken.")
        return value

    def validate_expires_at(self, value: datetime | None) -> datetime | None:
        """An expiry must be in the future."""
        if value is not None and value <= timezone.now():
            raise serializers.ValidationError("Must be in the future.")
        return value

    def update(self, instance: ShortURL, validated_data: dict[str, Any]) -> ShortURL:
        """Save the fields, then the tags (names, not ``Tag`` objects)."""
        tags = validated_data.pop("tags", None)
        instance = super().update(instance, validated_data)
        if tags is not None:
            set_tags(instance, tags)
        return instance


class CountryClicksSerializer(
    serializers.Serializer[Any]
):  # pylint: disable=abstract-method
    """One country and its number of clicks (empty country: unknown)."""

    country = serializers.CharField()
    total = serializers.IntegerField()


class ShortURLDetailSerializer(ShortURLSerializer):
    """One URL, plus click totals counted by the database (``annotate``)."""

    total_clicks = serializers.IntegerField(read_only=True)
    clicks_by_country = serializers.SerializerMethodField()

    class Meta(ShortURLSerializer.Meta):
        """Same fields plus the click totals."""

        fields = [*ShortURLSerializer.Meta.fields, "total_clicks", "clicks_by_country"]

    @extend_schema_field(CountryClicksSerializer(many=True))
    def get_clicks_by_country(self, url: ShortURL) -> list[dict[str, Any]]:
        """``[{"country": "Rwanda", "total": 3}, ...]``, most clicks first."""
        return url.clicks_by_country()


# Only describes the success body for Swagger; it never saves anything.
class ShortURLCreatedSerializer(
    serializers.Serializer[Any]
):  # pylint: disable=abstract-method
    """The success body: status code, message and the short URL as ``detail``."""

    status_code = serializers.IntegerField()
    message = serializers.CharField()
    detail = ShortURLSerializer()
