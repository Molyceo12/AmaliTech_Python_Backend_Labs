"""``GET /<short_code>/``: send the visitor to the original URL."""

from django.db.models import Q
from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.request import Request

from shortener.models import ShortURL
from shortener.services.clicks import record_click
from url_shortener.exceptions import ErrorSerializer, Gone


# A DRF view so a wrong code gets the same JSON error as the API.
@extend_schema(
    responses={
        302: OpenApiResponse(description="Redirect to the original URL."),
        404: ErrorSerializer,
        410: ErrorSerializer,
        500: ErrorSerializer,
    }
)
@api_view(["GET"])
@permission_classes([AllowAny])
def redirect_to_original(request: Request, short_code: str) -> HttpResponseRedirect:
    """302 to the saved URL (temporary, so later clicks still reach us).

    ``short_code`` may also be a custom alias. Unknown or switched off → 404,
    expired → 410. Every redirect is recorded as a click.
    """
    short_url = ShortURL.objects.filter(
        Q(short_code=short_code) | Q(custom_alias=short_code)
    ).first()
    # Switched off looks the same as unknown: nothing to see here.
    if short_url is None or not short_url.is_active:
        raise NotFound("Short code not found.")
    if short_url.is_expired:
        raise Gone("This short URL has expired.")
    record_click(short_url, request)
    return HttpResponseRedirect(short_url.original_url)
