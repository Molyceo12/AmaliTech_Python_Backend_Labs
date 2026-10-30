"""``GET /<short_code>/``: send the visitor to the original URL."""

from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404

from shortener.models import ShortURL


def redirect_to_original(request: HttpRequest, short_code: str) -> HttpResponseRedirect:
    """302 to the saved URL (temporary, so later clicks still reach us).

    An unknown code returns 404.
    """
    short_url = get_object_or_404(ShortURL, short_code=short_code)
    return HttpResponseRedirect(short_url.original_url)
