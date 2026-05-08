import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application

# Load .env
env_file = Path(__file__).resolve().parent.parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

env = os.environ.get('DJANGO_ENV', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env}')

application = get_wsgi_application()