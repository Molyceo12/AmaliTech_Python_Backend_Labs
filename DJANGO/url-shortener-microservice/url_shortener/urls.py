"""Root URL routes of the project."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="docs"),
    # Last: it ends with the catch-all short code route.
    path("", include("shortener.urls")),
]

# JSON instead of Django's HTML pages (used when DEBUG is False).
handler400 = "url_shortener.exceptions.bad_request"
handler403 = "url_shortener.exceptions.permission_denied"
handler404 = "url_shortener.exceptions.not_found"
handler500 = "url_shortener.exceptions.server_error"
