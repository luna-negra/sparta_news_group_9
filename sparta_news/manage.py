#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.core.management.utils import get_random_secret_key


def generate_secret_key():
    return get_random_secret_key()


def update_secret_key():
    # Check if SECRET_KEY is missing or empty
    if not os.getenv('SECRET_KEY'):
        os.environ.setdefault(key='SECRET_KEY',
                              value=generate_secret_key())


def main():
    update_secret_key()

    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sparta_news.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
