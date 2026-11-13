"""Production (Docker, server): debug pages off, HTTPS settings from ``.env``."""

from decouple import config

from url_shortener.settings.base import *  # noqa: F403  # pylint: disable=wildcard-import,unused-wildcard-import

DEBUG = False

# Off by default: local Docker serves plain http://localhost:8000 with these settings.
# A real server behind HTTPS turns them on in .env.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=False, cast=bool)
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = config(
    "SECURE_COOKIES", default=False, cast=bool
)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=0, cast=int)
