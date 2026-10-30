# Multi-stage build: the builder installs the dependencies, the runtime image
# gets only the installed packages and the code (no Poetry, no build tools).

# --- Stage 1: install the dependencies into /opt/venv ---
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Poetry goes into the builder's own Python; it installs the app's packages
# into the active /opt/venv, which is all the runtime stage copies.
RUN pip install poetry==2.5.1 && python -m venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /build
COPY pyproject.toml poetry.lock ./
# Main dependencies only: dev tools (pytest, mypy, ...) stay out of the image.
RUN poetry install --only main --no-root

# --- Stage 2: small runtime image ---
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=url_shortener.settings.prod

# Run as a normal user, not root.
RUN useradd --create-home --uid 1000 app
WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .
USER app

EXPOSE 8000
CMD ["gunicorn", "url_shortener.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
