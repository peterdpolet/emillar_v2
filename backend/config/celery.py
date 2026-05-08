import os
from pathlib import Path
from celery import Celery

# Load .env
env_file = Path(__file__).resolve().parent.parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

env = os.environ.get('DJANGO_ENV', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env}')

app = Celery('config')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()