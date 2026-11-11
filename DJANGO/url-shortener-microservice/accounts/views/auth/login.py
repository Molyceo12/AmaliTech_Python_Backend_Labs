"""``POST /api/v1/auth/login/``: email + password → tokens."""

from drf_spectacular.utils import extend_schema
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.serializers import LoginSerializer
from url_shortener.exceptions import ErrorSerializer


@extend_schema(
    responses={
        200: LoginSerializer,
        **dict.fromkeys([400, 401, 429, 500], ErrorSerializer),
    }
)
class LoginView(TokenObtainPairView):
    """Email + password → ``access`` (15 min) and ``refresh`` (1 day) tokens.

    5 tries per minute per IP; the 6th gets ``429``.
    """

    serializer_class = LoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"
    success_messages = {"POST": "Logged in."}
