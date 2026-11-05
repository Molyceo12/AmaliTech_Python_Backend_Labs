# URL Shortener Microservice

A URL shortener (like Bitly) built with Django and Django REST Framework. It
turns a long URL into a short code and redirects the short code back to the
original URL.

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Django](https://img.shields.io/badge/Django-5.2%20LTS-0C4B33)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)

## Architecture

```mermaid
graph TD
    Client((Client)) -->|HTTP request| Views

    subgraph Docker["Docker Compose"]
        subgraph Web["web container"]
            subgraph Gunicorn["Gunicorn 8000"]
                Views(Django Views)
            end
            Service(Short Code Service)
        end

        subgraph Db["db container"]
            DB[(PostgreSQL 5432<br/>postgres_data volume)]
        end
    end

    Views -->|create| Service
    Service --> DB
    Views -.->|redirect| DB
    Views -->|201 / 302 / JSON errors| Client
```

## Setup

```bash
git clone https://github.com/Molyceo12/AmaliTech_Python_Backend_Labs.git
cd AmaliTech_Python_Backend_Labs/DJANGO/url-shortener-microservice
cp .env.example .env              # SECRET_KEY, ALLOWED_HOSTS, POSTGRES_*
```

With Docker (Gunicorn + PostgreSQL 16):

```bash
docker compose up --build -d
```

Without Docker (SQLite):

```bash
python -m pip install poetry
python -m poetry install
python -m poetry run python manage.py migrate
python -m poetry run python manage.py runserver
```

Tests and code checks:

```bash
python -m poetry run python -m pytest --cov                 # run the tests with coverage
python -m poetry run python -m pre_commit run --all-files   # pre-commit hooks: ruff, Black, pylint, mypy
```

Swagger UI: http://localhost:8000/api/docs/

## Users

`accounts.User` (`AUTH_USER_MODEL`) extends Django's `AbstractUser`:

| Field | Rule |
|---|---|
| `email` | unique, required, saved lowercase; used to log in |
| `tier` | `free` (default), `premium` or `admin` |
| `is_premium` | set from `tier` on save (`premium` → True) |

`tier = admin` gives no admin rights: `is_staff` / `is_superuser` still decide that.

```bash
python -m poetry run python manage.py createsuperuser   # asks for email, username, password
```

Coming from Module 5? The user model changed, so start the dev databases fresh
once (lab data is lost):

```bash
rm db.sqlite3                  # SQLite
docker compose down -v         # Docker PostgreSQL volume
```

## URL data

| Model | Holds |
|---|---|
| `ShortURL` | `original_url`, `short_code`, `custom_alias`, `owner`, `is_active`, `expires_at`, `title`, `description`, `favicon`, `click_count`, `tags` |
| `Tag` | unique `name`, saved lowercase (many-to-many with `ShortURL`) |
| `Click` | one visit: time, IP, city, country, user agent, referrer (deleted with its URL) |

Named queries: `ShortURL.objects.active_urls()`, `.expired_urls()`, `.popular_urls()`.
Indexes on `created_at`, `expires_at` and `Click (short_url, clicked_at)`;
the database refuses an `expires_at` before `created_at`.

```bash
python -m poetry run python manage.py migrate   # adds the new tables and fields
```

## API endpoints

| Method | Route | What it does |
|---|---|---|
| `POST` | `/api/urls/` | creates a short URL (optional alias, expiry, title, description, tags) |
| `GET` | `/api/urls/` | lists short URLs, 20 per page |
| `GET` | `/api/urls/<short_code>/` | shows one URL with `total_clicks` |
| `PUT` / `PATCH` | `/api/urls/<short_code>/` | changes a URL |
| `DELETE` | `/api/urls/<short_code>/` | deletes a URL |
| `GET` | `/<short_code or alias>/` | redirects to the original URL and records a click |
| `GET` | `/api/docs/` | Swagger UI |
| `GET` | `/api/schema/` | OpenAPI schema |

List filters: `?status=active`, `?status=expired`, `?ordering=popular` (can be combined).

```bash
curl -X POST http://localhost:8000/api/urls/ \
     -H "Content-Type: application/json" \
     -d '{"original_url": "https://www.djangoproject.com/start/", "custom_alias": "django", "tags": ["docs"]}'
```

```json
{
  "status_code": 201,
  "message": "Short URL created.",
  "detail": {
    "original_url": "https://www.djangoproject.com/start/",
    "short_code": "M1gmaSk",
    "short_url": "http://localhost:8000/M1gmaSk/",
    "custom_alias": "django",
    "title": "",
    "description": "",
    "expires_at": null,
    "is_active": true,
    "tags": ["docs"],
    "owner": null,
    "click_count": 0,
    "created_at": "2026-11-05T12:23:36.052396Z",
    "updated_at": "2026-11-05T12:23:36.052412Z"
  }
}
```

`owner` is read-only and stays empty until login arrives (Module 7).

| Status | When |
|---|---|
| `200` | URL listed, shown or changed |
| `201` | short URL created |
| `204` | short URL deleted |
| `302` | redirect to the original URL |
| `400` | invalid URL, past expiry, reserved or bad alias, unknown filter |
| `404` | unknown or switched-off short code, unknown route |
| `405` | wrong HTTP method |
| `409` | custom alias already taken |
| `410` | short URL expired |
| `500` | server error (logged, never shown to the client) |

Errors: `{"status_code": 404, "detail": "Short code not found."}`
