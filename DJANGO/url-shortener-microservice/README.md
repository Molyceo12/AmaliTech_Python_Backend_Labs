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
3. [Settings](#settings)
4. [Testing](#testing)
5. [Project structure](#project-structure)

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

Then open http://localhost:8000/admin/.

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
(pytest, mypy, Black, Poetry) are not in the image. The admin page has no
styling in Docker (`DEBUG = False`, no static file server yet).

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

`tests/test_settings.py` checks that the apps are installed, `dev` and `prod`
set `DEBUG`, values come from the environment, a missing `SECRET_KEY` stops
the app, the WSGI/ASGI entry points and `manage.py` work, and the admin page
loads. `tests/test_database.py` checks SQLite without `DATABASE_URL` and
PostgreSQL from a `postgres://` URL. Coverage: 100 %.

Code style: every function has type hints (mypy strict with the Django and
DRF stubs) and every module, class and function has a docstring.

## Project structure

```
url-shortener-microservice/
├── url_shortener/              # Django project
│   ├── settings/               # base.py, dev.py, prod.py
│   ├── urls.py                 # root routes
│   ├── wsgi.py                 # WSGI entry point (Gunicorn)
│   └── asgi.py                 # ASGI entry point
├── shortener/                  # app: short URLs
│   ├── models/                 # database models
│   ├── serializers/            # request validation
│   ├── services/               # business logic
│   └── views/                  # API and redirect views
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
