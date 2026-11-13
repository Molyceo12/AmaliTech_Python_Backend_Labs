"""Input for ``POST /api/v1/account/upgrade/``."""

from typing import Any

from rest_framework import serializers

from accounts.models import User


class UpgradeSerializer(serializers.ModelSerializer[User]):
    """A ``payment_id`` (placeholder, not checked) and the ``plan`` to buy."""

    payment_id = serializers.CharField(max_length=100, write_only=True)
    plan = serializers.ChoiceField(choices=[User.Tier.PREMIUM], write_only=True)

    class Meta:
        """The client sends ``payment_id`` and ``plan``, and gets the new ``tier``."""

        model = User
        fields = ["payment_id", "plan", "tier"]
        read_only_fields = ["tier"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Only Free users can upgrade; Admin would lose its tier."""
        if self.instance is not None and self.instance.tier != User.Tier.FREE:
            raise serializers.ValidationError("Only Free users can upgrade.")
        return attrs

    def update(self, instance: User, validated_data: dict[str, Any]) -> User:
        """``save()`` also sets ``is_premium``."""
        instance.tier = validated_data["plan"]
        instance.save()
        return instance
