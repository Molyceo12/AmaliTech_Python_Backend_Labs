"""Auth routes; the project mounts them under ``/api/v1/auth/``."""

from django.urls import path

from accounts.views import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
]
