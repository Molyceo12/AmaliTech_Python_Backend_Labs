"""Input for ``POST /api/v1/auth/register/``."""

from typing import Any

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from accounts.models import User


class RegisterSerializer(serializers.ModelSerializer[User]):
    """A new account: email, username and a strong password.

    ``tier`` is only shown: every new user starts as ``free``.
    """

    # iexact: Bob@x.com and bob@x.com are the same account (emails are saved lowercase).
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="A user with this email already exists.",
            )
        ]
    )
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    class Meta:
        """The client sends email, username and password."""

        model = User
        fields = ["email", "username", "password", "tier"]
        read_only_fields = ["tier"]

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Run Django's password rules, e.g. not too short, not like the email."""
        user = User(email=attrs["email"], username=attrs["username"])
        try:
            validate_password(attrs["password"], user)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"password": error.messages}) from error
        return attrs

    def create(self, validated_data: dict[str, Any]) -> User:
        """``create_user`` saves the password hashed, never as plain text."""
        return User.objects.create_user(**validated_data)
