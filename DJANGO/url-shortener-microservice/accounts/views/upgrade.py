"""``POST /api/v1/account/upgrade/``: Free → Premium after a payment."""

from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.serializers import UpgradeSerializer
from url_shortener.exceptions import ErrorSerializer


@extend_schema(
    responses={
        200: UpgradeSerializer,
        **dict.fromkeys([400, 401, 500], ErrorSerializer),
    }
)
class UpgradeView(generics.GenericAPIView):  # type: ignore[type-arg]
    """Upgrade the logged-in Free user to Premium with a ``payment_id``."""

    serializer_class = UpgradeSerializer
    success_messages = {"POST": "Upgraded to Premium."}

    def post(self, request: Request) -> Response:
        """Save the new tier."""
        serializer = self.get_serializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
