"""Serializers that only describe responses for Swagger; they never save anything."""

from typing import Any

from rest_framework import serializers

from shortener.serializers.short_url import ShortURLSerializer


class CountryClicksSerializer(
    serializers.Serializer[Any]
):  # pylint: disable=abstract-method
    """One country and its number of clicks (empty country: unknown)."""

    country = serializers.CharField()
    total = serializers.IntegerField()


class ShortURLCreatedSerializer(
    serializers.Serializer[Any]
):  # pylint: disable=abstract-method
    """The success body: status code, message and the short URL as ``detail``."""

    status_code = serializers.IntegerField()
    message = serializers.CharField()
    detail = ShortURLSerializer()


class DayClicksSerializer(
    serializers.Serializer[Any]
):  # pylint: disable=abstract-method
    """One day and its number of clicks."""

    day = serializers.DateField()
    total = serializers.IntegerField()


class AnalyticsSerializer(
    serializers.Serializer[Any]
):  # pylint: disable=abstract-method
    """Clicks of one URL: total, per day (oldest first) and per country."""

    short_code = serializers.CharField()
    total_clicks = serializers.IntegerField()
    clicks_per_day = DayClicksSerializer(many=True)
    clicks_by_country = CountryClicksSerializer(many=True)
