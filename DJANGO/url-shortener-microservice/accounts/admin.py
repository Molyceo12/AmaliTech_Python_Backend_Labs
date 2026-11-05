"""Django admin for users: Django's ``UserAdmin`` plus the tier."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import User


@admin.register(User)
class AccountUserAdmin(UserAdmin):  # type: ignore[type-arg]
    """Users listed by email; the add form asks for the email too."""

    list_display = ("email", "username", "tier", "is_premium", "is_staff")
    ordering = ("email",)
    # is_premium follows tier (see User.save), so it is shown, not edited.
    readonly_fields = ("is_premium",)
    fieldsets = (
        *(UserAdmin.fieldsets or ()),
        ("Tier", {"fields": ("tier", "is_premium")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
