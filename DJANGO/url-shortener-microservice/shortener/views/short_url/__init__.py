"""``/api/v1/urls/`` views: the list + create, and one URL's detail."""

from shortener.views.short_url.get_delete_update_shorturl import ShortURLDetailView
from shortener.views.short_url.list_create import ShortURLListCreateView

__all__ = ["ShortURLDetailView", "ShortURLListCreateView"]
