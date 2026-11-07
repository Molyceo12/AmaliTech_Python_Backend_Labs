"""``GET /<short_code>/``: send the visitor to the original URL."""

from django.http import HttpResponseRedirect
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.request import Request

from shortener.models import ShortURL
from url_shortener.exceptions import ErrorSerializer


# A DRF view so a wrong code gets the same JSON error as the API.
# Swagger documents it, but only a browser follows the redirect.
@extend_schema(
    responses={
        302: OpenApiResponse(description="Redirect to the original URL."),
        404: ErrorSerializer,
        500: ErrorSerializer,
    }
)
@api_view(["GET"])
def redirect_to_original(request: Request, short_code: str) -> HttpResponseRedirect:
    """302 to the saved URL (temporary, so later clicks still reach us).

    An unknown code returns the shared JSON error with status 404.
    """
    short_url = ShortURL.objects.filter(short_code=short_code).first()
    if short_url is None:
        raise NotFound("Short code not found.")
    return HttpResponseRedirect(short_url.original_url)
