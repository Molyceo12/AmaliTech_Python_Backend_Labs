# URL Shortener Microservice

A URL shortener service (like Bitly) built with Django and Django REST
Framework. It turns a long URL into a short code and redirects the short code
back to the original URL.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Django](https://img.shields.io/badge/Django-5.2%20LTS-0C4B33)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)
![mypy](https://img.shields.io/badge/mypy-strict-blue)

## Table of contents

1. [Setup](#setup)
2. [Docker](#docker)
3. [API](#api)
4. [Settings](#settings)
5. [Testing](#testing)
6. [Project structure](#project-structure)

## Setup

Requires Python 3.11+.

```bash
git clone https://github.com/Molyceo12/AmaliTech_Python_Backend_Labs.git
cd AmaliTech_Python_Backend_Labs/DJANGO/url-shortener-microservice

cp .env.example .env              # local settings (SECRET_KEY, ALLOWED_HOSTS, POSTGRES_*)

# with Poetry (creates .venv/ inside the project)
python -m pip install poetry
python -m poetry install
python -m poetry run python manage.py migrate
python -m poetry run python manage.py runserver
```

Then open the Swagger UI at http://localhost:8000/api/docs/.

Without Poetry (`requirements.txt` is the pinned list exported from Poetry):

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker

Runs the app with Gunicorn and PostgreSQL 16. Requires
[Docker Desktop](https://www.docker.com/products/docker-desktop/) and a `.env`
file (`cp .env.example .env`).

```bash
docker compose up --build -d      # build and start in the background
docker compose logs -f web        # follow the app logs
docker compose down               # stop (data is kept)
docker compose down -v            # stop and delete the database data
```

Then open http://localhost:8000/admin/.

| Service | What it does |
|---|---|
| `db` | PostgreSQL 16; data in the `postgres_data` volume. Its port is not published, so a local PostgreSQL can keep 5432 |
| `web` | waits for `db` to be healthy, runs `migrate`, then starts Gunicorn on port 8000 |

The `Dockerfile` has two stages: `builder` installs the main dependencies
with Poetry into `/opt/venv`, and `runtime` copies only `/opt/venv` and the
code into a `python:3.12-slim` image that runs as a non-root user. Dev tools
(pytest, mypy, Black, Poetry) are not in the image. The API answers on the
same port, e.g. http://localhost:8000/api/docs/. The admin page has no
styling in Docker (`DEBUG = False`, no static file server yet).

## API

| Method | Route | What it does |
|---|---|---|
| `POST` | `/api/urls/` | saves a long URL under a new short code (`201`; invalid URL → `400`) |
| `GET` | `/<short_code>/` | redirects (`302`) to the original URL (unknown code → `404`) |
| `GET` | `/api/docs/` | Swagger UI ([drf-spectacular](https://drf-spectacular.readthedocs.io/)) |
| `GET` | `/api/schema/` | OpenAPI schema |

```bash
curl -X POST http://localhost:8000/api/urls/ \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://www.djangoproject.com/start/"}'
```

Success (`201`): status code, message, and the saved short URL in `detail`.

```json
{
  "status_code": 201,
  "message": "Short URL created.",
  "detail": {
    "original_url": "https://www.djangoproject.com/start/",
    "short_code": "M1gmaSk",
    "short_url": "http://localhost:8000/M1gmaSk/",
    "created_at": "2026-10-30T12:23:36.052396Z"
  }
}
```

Errors: always `status_code` and `detail` (custom DRF exception handler in
`url_shortener/exceptions.py`). Field errors keep their field name:

```json
{"status_code": 400, "detail": {"original_url": ["Enter a valid URL."]}}
{"status_code": 404, "detail": "Short code not found."}
{"status_code": 405, "detail": "Method \"GET\" not allowed."}
```

Opening `short_url` sends the browser to the original URL. Codes are 7 random
letters and digits (`secrets`); a code already in use is drawn again. The
redirect is temporary (`302`) so later clicks still reach the service.

## Settings

Settings live in `url_shortener/settings/` and read secrets from environment
variables or `.env` (python-decouple), never from the code:

| File | Used by | What it sets |
|---|---|---|
| `base.py` | every environment | apps, middleware; `SECRET_KEY`, `ALLOWED_HOSTS` and `DATABASE_URL` from `.env` |
| `dev.py` | `manage.py` (default) | `DEBUG = True` |
| `prod.py` | `wsgi.py` / `asgi.py` (default) | `DEBUG = False` |

`DJANGO_SETTINGS_MODULE` overrides the default, e.g.
`DJANGO_SETTINGS_MODULE=url_shortener.settings.prod`.

| Variable | Required | Example |
|---|---|---|
| `SECRET_KEY` | yes (the app stops without it) | `local-dev-only-change-me` |
| `ALLOWED_HOSTS` | no (default `localhost`) | `localhost,127.0.0.1` |
| `DATABASE_URL` | no (default SQLite `db.sqlite3`); `docker-compose.yml` sets it | `postgres://user:pass@db:5432/name` |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | for Docker only | `shortener`, `shortener`, `shortener-local` |

## Testing

```bash
python -m poetry run python -m pytest --cov                   # tests + coverage
python -m poetry run python -m pre_commit run --all-files     # ruff, Black, pylint, mypy
```

| File | Checks |
|---|---|
| `test_settings.py` | apps installed, `DEBUG` per environment, values from the environment, missing `SECRET_KEY` stops the app, WSGI/ASGI and `manage.py` work |
| `test_database.py` | SQLite without `DATABASE_URL`, PostgreSQL from a `postgres://` URL |
| `test_short_codes.py` | code format, saving a URL, a taken code is drawn again |
| `test_shorten_api.py` | `201` body with `status_code`, `message` and the short URL in `detail`, `400` for an invalid or missing URL, `405` error body |
| `test_redirect.py` | `302` to the original URL, JSON `404` for an unknown code, `admin/` still works |
| `test_api_docs.py` | schema lists the `201` and `400` responses of `/api/urls/`, Swagger UI loads |
| `test_exceptions.py` | non-API errors are left to Django |

Coverage: 100 %.

Code style: every function has type hints (mypy strict with the Django and
DRF stubs) and every module, class and function has a docstring.

## Project structure

```
url-shortener-microservice/
├── url_shortener/              # Django project
│   ├── settings/               # base.py, dev.py, prod.py
│   ├── urls.py                 # admin, API docs, shortener routes
│   ├── exceptions.py           # JSON error body: status_code + detail
│   ├── wsgi.py                 # WSGI entry point (Gunicorn)
│   └── asgi.py                 # ASGI entry point
├── shortener/                  # app: short URLs
│   ├── models/                 # ShortURL
│   ├── serializers/            # validates original_url, returns short_url
│   ├── services/               # short code creation
│   ├── views/                  # POST /api/urls/, GET /<short_code>/
│   ├── migrations/
│   └── urls.py                 # the app's routes
├── accounts/                   # app: users
│   └── models/
├── tests/
├── manage.py
├── Dockerfile                  # multi-stage: builder + runtime
├── docker-compose.yml          # web + db (PostgreSQL 16)
├── .dockerignore
├── .env.example
├── pyproject.toml, poetry.lock, poetry.toml, requirements.txt
└── README.md
```
