"""Routes of the shortener app: the API and the redirect."""

from django.urls import path

from shortener.views import ShortURLCreateView, redirect_to_original

app_name = "shortener"

urlpatterns = [
    path("api/urls/", ShortURLCreateView.as_view(), name="create"),
    # Catch-all for codes, so it must stay after every other route.
    path("<str:short_code>/", redirect_to_original, name="redirect"),
]
