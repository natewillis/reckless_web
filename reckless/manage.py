#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import environ

def main():
    """Run administrative tasks."""
    # Load environment variables from .env file
    env = environ.Env()
    environ.Env.read_env()

    # Default to development settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'reckless.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
