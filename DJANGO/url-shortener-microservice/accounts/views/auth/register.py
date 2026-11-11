"""``POST /api/v1/auth/register/``: create an account."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny

from accounts.serializers import RegisterSerializer
from url_shortener.exceptions import ErrorSerializer


@extend_schema(
    responses={201: RegisterSerializer, 400: ErrorSerializer, 500: ErrorSerializer}
)
class RegisterView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Create an account. Log in afterwards to get tokens."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    success_messages = {"POST": "Account created."}
