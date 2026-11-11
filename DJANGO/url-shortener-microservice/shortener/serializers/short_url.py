"""Validate short URL input and show saved short URLs."""

from datetime import datetime
from typing import Any

from django.db.models import Q
from django.utils import timezone
from rest_framework import serializers

from shortener.models import ShortURL
from shortener.serializers.fields import TagNamesField
from shortener.services.short_codes import set_tags
from url_shortener.exceptions import Conflict

# Routes that live at the top level, so an alias can't take their place.
RESERVED_ALIASES = {"api", "admin"}


class ShortURLSerializer(serializers.ModelSerializer[ShortURL]):
    """Takes the URL and its details; returns them with the code and link."""

    short_url = serializers.SerializerMethodField()
    custom_alias = serializers.RegexField(
        r"^[A-Za-z0-9-]+$", max_length=50, required=False, allow_null=True
    )
    tags = TagNamesField(required=False)
    # The view sets the owner from the logged-in user; the client never does.
    owner = serializers.EmailField(source="owner.email", read_only=True)

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
