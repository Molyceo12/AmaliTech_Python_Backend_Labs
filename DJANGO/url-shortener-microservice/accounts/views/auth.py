"""``/api/v1/auth/``: register, log in, refresh the access token."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts.serializers import LoginSerializer, RegisterSerializer
from url_shortener.exceptions import ErrorSerializer

ERRORS = {400: ErrorSerializer, 500: ErrorSerializer}
TOKEN_ERRORS = {**ERRORS, 401: ErrorSerializer}


@extend_schema(responses={201: RegisterSerializer, **ERRORS})
class RegisterView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Create an account. Log in afterwards to get tokens."""

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    success_messages = {"POST": "Account created."}


@extend_schema(responses={200: LoginSerializer, 429: ErrorSerializer, **TOKEN_ERRORS})
class LoginView(TokenObtainPairView):
    """Email + password → ``access`` (15 min) and ``refresh`` (1 day) tokens.

    5 tries per minute per IP; the 6th gets ``429``.
    """

    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
    success_messages = {"POST": "Logged in."}


@extend_schema(responses={200: TokenRefreshView.serializer_class, **TOKEN_ERRORS})
class RefreshView(TokenRefreshView):
    """A ``refresh`` token → a new ``access`` token."""

    success_messages = {"POST": "Token refreshed."}
