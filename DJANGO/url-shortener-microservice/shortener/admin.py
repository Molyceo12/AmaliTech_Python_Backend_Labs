"""Show short URLs, tags and clicks in the Django admin."""

from django.contrib import admin

from shortener.models import Click, ShortURL, Tag


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Short URLs with their owner, status and clicks."""

    list_display = ["short_code", "original_url", "owner", "is_active", "click_count"]
    list_filter = ["is_active", "tags"]
    search_fields = ["short_code", "custom_alias", "original_url"]


admin.site.register(Tag)
admin.site.register(Click)
