"""Settings shared by every environment.

Secrets and per-machine values come from environment variables or a ``.env``
file (see ``.env.example``), never from the code.
"""

from datetime import timedelta
from pathlib import Path

import dj_database_url
from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# No default: the app must not start with a guessable key.
SECRET_KEY: str = config("SECRET_KEY")
DEBUG = False
ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "shortener",
    "accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "url_shortener.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "url_shortener.wsgi.application"

# One URL holds every database setting: Docker sets a postgres:// URL,
# without one the app uses a local SQLite file.
DATABASES = {
    "default": config(
        "DATABASE_URL",
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        cast=dj_database_url.parse,
    )
}

AUTH_USER_MODEL = "accounts.User"

# Password of the seed_dev user; empty means that user can't log in.
SEED_USER_PASSWORD: str = config("SEED_USER_PASSWORD", default="")

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": f"django.contrib.auth.password_validation.{name}"}
    for name in (
        "UserAttributeSimilarityValidator",
        "MinimumLengthValidator",
        "CommonPasswordValidator",
        "NumericPasswordValidator",
    )
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Print logs (and server error tracebacks) to the console, also with DEBUG off,
# so `docker compose logs web` shows them.
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "plain": {"format": "{asctime} {levelname} {name}: {message}", "style": "{"}
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_DIR / "app.log",
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "formatter": "plain",
            "encoding": "utf-8",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication"
    ],
    # Every API needs a token; open views say permission_classes = [AllowAny].
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_RENDERER_CLASSES": ["url_shortener.renderers.EnvelopeJSONRenderer"],
    "EXCEPTION_HANDLER": "url_shortener.exceptions.json_exception_handler",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # Views pick a scope with throttle_scope. "login": 5 tries per minute per IP,
    # against password guessing. Counted in local memory (Redis in Module 8).
    "DEFAULT_THROTTLE_RATES": {"login": "5/min"},
}
# JWTs are signed with SECRET_KEY. A short access token limits the harm of a stolen
# one; the refresh token gets a new access token without logging in again.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}
SPECTACULAR_SETTINGS = {
    "TITLE": "URL Shortener API",
    "DESCRIPTION": "Turn a long URL into a short code and redirect it back.",
    "VERSION": "1.0.0",
}
