"""Public redirect ``/<short_code>/``: never versioned, so short links never change."""

from django.urls import path

from shortener.views import redirect_to_original

urlpatterns = [
    path("<str:short_code>/", redirect_to_original, name="redirect"),
]
