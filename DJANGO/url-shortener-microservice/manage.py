#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""

import os
import sys


def main() -> None:
    """Run an administrative task, e.g. ``python manage.py runserver``."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "url_shortener.settings")
    from django.core.management import (  # pylint: disable=import-outside-toplevel
        execute_from_command_line,
    )

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
