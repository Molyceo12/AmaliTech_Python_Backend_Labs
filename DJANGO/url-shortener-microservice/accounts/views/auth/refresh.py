"""``POST /api/v1/auth/refresh/``: refresh token → new access token."""

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.views import TokenRefreshView

from url_shortener.exceptions import ErrorSerializer


@extend_schema(
    responses={
        200: TokenRefreshView.serializer_class,
        **dict.fromkeys([400, 401, 500], ErrorSerializer),
    }
)
class RefreshView(TokenRefreshView):
    """A ``refresh`` token → a new ``access`` token."""

    success_messages = {"POST": "Token refreshed."}
