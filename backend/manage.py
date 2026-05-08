# manage.py
import os
import sys
from pathlib import Path


def main():
    # Load .env file if it exists
    env_file = Path(__file__).resolve().parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)

    env = os.environ.get('DJANGO_ENV', 'development')
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        f'config.settings.{env}'
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you on the right virtualenv?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
