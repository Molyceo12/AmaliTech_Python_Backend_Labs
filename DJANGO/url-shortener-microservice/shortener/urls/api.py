"""API routes; the project mounts them under ``/api/v1/``."""

from django.urls import path

from shortener.views import ShortURLCreateView

urlpatterns = [
    path("urls/", ShortURLCreateView.as_view(), name="url-create"),
]
