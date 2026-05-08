"""config/asgi.py"""
import os
from pathlib import Path
from django.core.asgi import get_asgi_application

# Load .env
env_file = Path(__file__).resolve().parent.parent / '.env'
if env_file.exists():
    from dotenv import load_dotenv
    load_dotenv(env_file)

env = os.environ.get('DJANGO_ENV', 'development')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env}')

# Must be called before importing anything that uses Django models
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from chat.middleware import JWTAuthMiddleware
import chat.routing

from django.conf import settings

if settings.DEBUG:
    application = ProtocolTypeRouter({
        'http': django_asgi_app,
        'websocket': JWTAuthMiddleware(
            URLRouter(chat.routing.websocket_urlpatterns)
        ),
    })
else:
    application = ProtocolTypeRouter({
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            JWTAuthMiddleware(
                URLRouter(chat.routing.websocket_urlpatterns)
            )
        ),
    })