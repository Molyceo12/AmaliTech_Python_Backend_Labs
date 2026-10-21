# Log File Analyzer

A command-line tool that parses web server access logs (Apache/Nginx format)
with regular expressions and builds analytics reports using functional
programming, generators, decorators, `itertools` and `functools`.

## Setup

Requires Python 3.11+.

```bash
cd AmaliTech_Python_Backend_Labs/ADVANCED_PYTHON/log-file-analyzer
python -m pip install poetry
python -m poetry install
```

## Testing

```bash
python -m poetry run pytest --cov
```
