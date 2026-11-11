"""Auth routes; the project mounts them under ``/api/v1/auth/``."""

from django.urls import path

from accounts.views import LoginView, RefreshView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
]
