"""API routes; the project mounts them under ``/api/v1/``."""

from django.urls import path

from shortener.views import AnalyticsView, ShortURLDetailView, ShortURLListCreateView

urlpatterns = [
    path("urls/", ShortURLListCreateView.as_view(), name="url-list"),
    path("urls/<str:short_code>/", ShortURLDetailView.as_view(), name="url-detail"),
    path("analytics/<str:short_code>/", AnalyticsView.as_view(), name="url-analytics"),
]
