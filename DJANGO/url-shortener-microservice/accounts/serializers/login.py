"""Input for ``POST /api/v1/auth/login/``."""

from typing import Any

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


# Only checks a login and returns tokens; it never saves anything.
class LoginSerializer(TokenObtainPairSerializer):  # pylint: disable=abstract-method
    """Email + password → access and refresh tokens.

    Emails are saved lowercase, so ``Ann@Example.com`` must log in too.
    """

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        """Lowercase the email, then let simplejwt check the password."""
        attrs[self.username_field] = attrs[self.username_field].lower()
        return super().validate(attrs)
