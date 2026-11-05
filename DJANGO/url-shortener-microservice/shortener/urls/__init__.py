"""Routes of the shortener app, one module per feature."""

from shortener.urls.short_url import urlpatterns as short_url_patterns

app_name = "shortener"

# short_url_patterns ends with the catch-all code route, so it stays last.
urlpatterns = [*short_url_patterns]
