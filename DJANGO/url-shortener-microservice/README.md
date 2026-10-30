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
2. [Settings](#settings)
3. [Testing](#testing)
4. [Project structure](#project-structure)

## Setup

Requires Python 3.11+.

```bash
git clone https://github.com/Molyceo12/AmaliTech_Python_Backend_Labs.git
cd AmaliTech_Python_Backend_Labs/DJANGO/url-shortener-microservice

cp .env.example .env              # local settings (SECRET_KEY, ALLOWED_HOSTS)

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

## Settings

Settings live in `url_shortener/settings/` and read secrets from environment
variables or `.env` (python-decouple), never from the code:

| File | Used by | What it sets |
|---|---|---|
| `base.py` | every environment | apps, middleware, database; `SECRET_KEY` and `ALLOWED_HOSTS` from `.env` |
| `dev.py` | `manage.py` (default) | `DEBUG = True` |
| `prod.py` | `wsgi.py` / `asgi.py` (default) | `DEBUG = False` |

`DJANGO_SETTINGS_MODULE` overrides the default, e.g.
`DJANGO_SETTINGS_MODULE=url_shortener.settings.prod`.

| Variable | Required | Example |
|---|---|---|
| `SECRET_KEY` | yes (the app stops without it) | `local-dev-only-change-me` |
| `ALLOWED_HOSTS` | no (default `localhost`) | `localhost,127.0.0.1` |

## Testing

```bash
python -m poetry run python -m pytest --cov                   # tests + coverage
python -m poetry run python -m pre_commit run --all-files     # ruff, Black, pylint, mypy
```

`tests/test_settings.py` checks that the apps are installed, `dev` and `prod`
set `DEBUG`, values come from the environment, a missing `SECRET_KEY` stops
the app, the WSGI/ASGI entry points and `manage.py` work, and the admin page
loads. Coverage: 100 %.

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
├── .env.example
├── pyproject.toml, poetry.lock, poetry.toml, requirements.txt
└── README.md
```
