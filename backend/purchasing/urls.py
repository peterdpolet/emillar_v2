from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchase-order')
router.register(r'goods-receipts', views.GoodsReceiptViewSet, basename='goods-receipt')
router.register(r'items', views.ItemViewSet, basename='item')

urlpatterns = [
    path('', include(router.urls)),
]