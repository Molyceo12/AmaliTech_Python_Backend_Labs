"""WSGI entry point (used by Gunicorn): exposes ``application``."""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "url_shortener.settings.prod")

application = get_wsgi_application()
