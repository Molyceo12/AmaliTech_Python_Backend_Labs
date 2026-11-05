"""Database models for short URLs."""

from shortener.models.click import Click
from shortener.models.short_url import ShortURL
from shortener.models.tag import Tag

__all__ = ["Click", "ShortURL", "Tag"]
