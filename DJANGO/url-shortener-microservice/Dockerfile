# Two stages: Poetry and its leftovers stay in the builder; the runtime image
# gets only the installed packages and the code.

FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install poetry==2.5.1 && python -m venv /opt/venv

# Poetry installs into the active venv, so activate /opt/venv first.
ENV VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /build

# Dependency files before the code: the install layer stays cached until they change.
COPY pyproject.toml poetry.lock ./

# --no-root: the code is copied in the runtime stage, not installed as a package.
RUN poetry install --only main --no-root

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH" \
    DJANGO_SETTINGS_MODULE=url_shortener.settings.prod

# Don't run as root: a break-in gets a normal user's rights only.
RUN useradd --create-home --uid 1000 app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app . .

# The app user writes logs/app.log; the app_logs volume is mounted here.
RUN mkdir -p /app/logs && chown app:app /app/logs

USER app

EXPOSE 8000

CMD ["gunicorn", "url_shortener.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
