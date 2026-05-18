from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .print_views import print_label

from . import views

router = DefaultRouter()
router.register(r'items',     views.ItemViewSet,    basename='item')
router.register(r'colors',   views.ColorViewSet,  basename='color')
router.register(r'clarities', views.ClarityViewSet, basename='clarity')
router.register(r'cuts',      views.CutViewSet,     basename='cut')
router.register(r'movements', views.StockMovementViewSet, basename='movement')

urlpatterns = [
    path('', include(router.urls)),
    path('print-label/', print_label),
]