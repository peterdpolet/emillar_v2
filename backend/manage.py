import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def main():
    base_dir = Path(__file__).resolve().parent

    # Load .env.production if it exists, otherwise .env.development
    env_file = base_dir.parent / '.env.production'
    if not env_file.exists():
        env_file = base_dir.parent / '.env.development'

    load_dotenv(env_file)

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
