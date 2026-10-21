"""Build the sample access logs in ``data/``.

Run from the lab folder: ``python scripts/generate_logs.py``. A fixed random
seed gives the same files on every run, so tests can rely on them.
"""

import random
from datetime import UTC, datetime, timedelta
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
SEED = 42

IPS = [f"192.168.1.{n}" for n in range(10, 40)] + [
    "10.0.0.5",
    "10.0.0.7",
    "172.16.4.20",
    "203.0.113.9",
    "198.51.100.23",
]
URLS = [
    "/",
    "/index.html",
    "/about",
    "/contact",
    "/products",
    "/products/42",
    "/products/17?ref=home",
    "/search?q=python",
    "/search?q=regex&page=2",
    "/login",
    "/logout",
    "/api/v1/orders",
    "/api/v1/users/7",
    "/static/css/site.css",
    "/static/js/app.js",
    "/images/logo.png",
    "/admin",
    "/old-page",
]
METHODS = ["GET"] * 8 + ["POST"] * 2 + ["PUT", "DELETE"]
# Mostly successful requests, with redirects, client and server errors.
STATUSES = [200] * 14 + [201, 204, 301, 302, 304, 400, 401, 403, 404, 404, 500, 503]
REFERRERS = ["-", "https://www.google.com/", "https://example.com/", "-"]
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/130.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Firefox/131.0",
    "curl/8.9.1",
    "python-requests/2.32.3",
]

# Bad and unusual lines mixed with good ones, for the parser tests.
MALFORMED_LINES = [
    '192.168.1.10 - - [20/Oct/2026:08:00:01 +0000] "GET / HTTP/1.1" 200 512 '
    '"-" "curl/8.9.1"',
    '10.0.0.5 - - [20/Oct/2026:08:00:02 +0000] "POST /login HTTP/1.0" 302 -',
    "this is not a log line",
    "",
    '192.168.1.11 - - [20/Oct/2026:08:00:03 +0000] "GET / HTTP/1.1" 2000 512',
    '192.168.1.12 - - 20/Oct/2026:08:00:04 +0000 "GET / HTTP/1.1" 200 512',
    '192.168.1.13 - - [32/Oct/2026:08:00:05 +0000] "GET / HTTP/1.1" 200 512',
    "192.168.1.14 - - [20/Oct/2026:08:00:06 +0000] GET / HTTP/1.1 200 512",
    # Extra spaces and tabs: still valid once the whitespace is cleaned.
    '   192.168.1.15  -  -\t[20/Oct/2026:08:00:07 +0000]  "GET /a HTTP/1.1"  404  0',
    "192.168.1.16 - - [20/Oct/2026:08:00:08 +0000] "
    '"DELETE /api/v1/users/7 HTTP/2" 204 -',
]


def log_line(rng: random.Random, when: datetime) -> str:
    """Return one combined-format line for a random request at ``when``."""
    status = rng.choice(STATUSES)
    size = "-" if status in (204, 304) else str(rng.randint(120, 52_000))
    return (
        f"{rng.choice(IPS)} - - [{when.strftime('%d/%b/%Y:%H:%M:%S %z')}] "
        f'"{rng.choice(METHODS)} {rng.choice(URLS)} HTTP/1.1" {status} {size} '
        f'"{rng.choice(REFERRERS)}" "{rng.choice(USER_AGENTS)}"'
    )


def day_of_logs(rng: random.Random, day: datetime, count: int) -> list[str]:
    """Return ``count`` lines spread over one day, oldest first."""
    seconds = sorted(rng.randrange(24 * 60 * 60) for _ in range(count))
    return [log_line(rng, day + timedelta(seconds=s)) for s in seconds]


def write_lines(path: Path, lines: list[str]) -> None:
    """Write lines with Unix line endings and a final newline."""
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    """Write ``access.log``, ``access_2.log`` and ``malformed.log``."""
    rng = random.Random(SEED)
    first_day = datetime(2026, 10, 20, tzinfo=UTC)
    DATA.mkdir(exist_ok=True)
    write_lines(DATA / "access.log", day_of_logs(rng, first_day, 1200))
    write_lines(
        DATA / "access_2.log", day_of_logs(rng, first_day + timedelta(days=1), 300)
    )
    write_lines(DATA / "malformed.log", MALFORMED_LINES)
    print(f"Sample logs written to {DATA}")


if __name__ == "__main__":
    main()
