"""API and redirect views for short URLs."""

from shortener.views.redirect import redirect_to_original
from shortener.views.short_url import ShortURLCreateView

__all__ = ["ShortURLCreateView", "redirect_to_original"]
