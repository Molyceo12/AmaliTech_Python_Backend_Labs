"""Root URL routes of the project.

The API and redirect routes are added in branch 3.
"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]
