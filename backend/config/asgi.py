"""config/asgi.py"""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

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
