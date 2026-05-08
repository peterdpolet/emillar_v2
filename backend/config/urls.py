"""config/urls.py"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api/auth/', include('accounts.urls')),    # TOTP endpoints
    path('api/chat/', include('chat.urls')),
    path('api/partners/', include('partners.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/orders/', include('orders.urls')),          # uncommented
    path('api/purchasing/', include('purchasing.urls')),  # add this
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)