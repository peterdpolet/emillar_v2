"""accounts/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path('login/',        views.login,        name='auth-login'),
    path('me/',           views.me,           name='auth-me'),
    path('totp/setup/',   views.totp_setup,   name='totp-setup'),
    path('totp/verify/',  views.totp_verify,  name='totp-verify'),
    path('totp/disable/', views.totp_disable, name='totp-disable'),
]
