"""Custom serializer fields."""

from typing import Any

from rest_framework import serializers


class TagNamesField(serializers.ListField):
    """Tags in and out as names, e.g. ``["docs", "python"]``."""

    child = serializers.CharField(max_length=50)

    def to_representation(self, data: Any) -> list[str]:
        """``data`` is the URL's tags manager; ``all()`` uses the prefetch."""
        return [tag.name for tag in data.all()]
