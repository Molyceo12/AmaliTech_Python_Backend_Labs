"""Validate a long URL and show the saved short URL."""

from typing import Any

from rest_framework import serializers

from shortener.models import ShortURL


class ShortURLSerializer(serializers.ModelSerializer[ShortURL]):
    """Takes ``original_url``; returns the code and the full short link."""

    short_url = serializers.SerializerMethodField()

    class Meta:
        """Only ``original_url`` is sent by the client."""

        model = ShortURL
        fields = ["original_url", "short_code", "short_url", "created_at"]
        read_only_fields = ["short_code", "created_at"]

    def get_short_url(self, obj: ShortURL) -> str:
        """Full link to open, e.g. ``http://localhost:8000/aB3xY9z/``."""
        path = f"/{obj.short_code}/"
        request: Any = self.context.get("request")
        return str(request.build_absolute_uri(path)) if request else path


class ShortURLCreatedSerializer(ShortURLSerializer):
    """The success body: the short URL plus its status code."""

    status_code = serializers.IntegerField(read_only=True)

    class Meta(ShortURLSerializer.Meta):
        """``status_code`` first, like in the error body."""

        fields = ["status_code", *ShortURLSerializer.Meta.fields]
