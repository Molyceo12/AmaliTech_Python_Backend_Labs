"""Root URL routes of the project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Last: it ends with the catch-all short code route.
    path("", include("shortener.urls")),
]
