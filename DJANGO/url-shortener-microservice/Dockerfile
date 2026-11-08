# Multi-stage build: the builder installs the dependencies, the runtime image
# gets only the installed packages and the code (no Poetry, no build tools).

# --- Stage 1: install the dependencies into /opt/venv ---

# Small Python image; this stage is named "builder".
FROM python:3.12-slim AS builder

# pip: keep no download cache, skip the update check (smaller, quieter).
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install Poetry and create the venv the app's packages go into.
RUN pip install poetry==2.5.1 && python -m venv /opt/venv

# Make /opt/venv the active venv, so Poetry installs into it.
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Work in /build.
WORKDIR /build

# Copy only the dependency files (the code comes later).
COPY pyproject.toml poetry.lock ./

# Install the main packages only: no dev tools, not the app itself.
RUN poetry install --only main --no-root

# --- Stage 2: small runtime image ---

# Start again from a clean small image; this stage is named "runtime".
FROM python:3.12-slim AS runtime

# No .pyc files, logs shown at once, use the venv, prod settings.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=url_shortener.settings.prod

# Create a normal user "app" (safer than root).
RUN useradd --create-home --uid 1000 app

# Work in /app.
WORKDIR /app

# Take only the installed packages from the builder stage.
COPY --from=builder /opt/venv /opt/venv

# Copy the code, owned by the app user.
COPY --chown=app:app . .

# Folder for logs/app.log, writable by the app user (a volume keeps it).
RUN mkdir -p /app/logs && chown app:app /app/logs

# Run everything below as the app user.
USER app

# The app listens on port 8000.
EXPOSE 8000

# Start Gunicorn with 3 workers on port 8000.
CMD ["gunicorn", "url_shortener.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
