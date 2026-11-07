"""Redirect route: ``/<short_code>/``, kept short and unversioned."""

from django.urls import path

from shortener.views import redirect_to_original

urlpatterns = [
    path("<str:short_code>/", redirect_to_original, name="redirect"),
]
