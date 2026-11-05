"""Short URL routes: create a code, and redirect a code to its URL."""

from django.urls import path

from shortener.views import ShortURLCreateView, redirect_to_original

urlpatterns = [
    path("api/urls/", ShortURLCreateView.as_view(), name="create"),
    # Catch-all for codes, so it must stay after every other route.
    path("<str:short_code>/", redirect_to_original, name="redirect"),
]
