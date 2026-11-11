"""``/api/v1/auth/``: register."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from accounts.serializers import RegisterSerializer
from url_shortener.exceptions import ErrorSerializer

ERRORS = {400: ErrorSerializer, 500: ErrorSerializer}


@extend_schema(responses={201: RegisterSerializer, **ERRORS})
class RegisterView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Create an account. Log in afterwards to get tokens."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    success_messages = {"POST": "Account created."}
