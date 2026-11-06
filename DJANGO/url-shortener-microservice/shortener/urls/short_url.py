"""Short URL routes: manage URLs, and redirect a code to its URL."""

from django.urls import path

from shortener.views import (
    ShortURLDetailView,
    ShortURLListCreateView,
    redirect_to_original,
)

urlpatterns = [
    path("api/v1/urls/", ShortURLListCreateView.as_view(), name="list"),
    path("api/v1/urls/<str:short_code>/", ShortURLDetailView.as_view(), name="detail"),
    # Catch-all for codes, so it must stay after every other route.
    path("<str:short_code>/", redirect_to_original, name="redirect"),
]
