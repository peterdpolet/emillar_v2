from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'purchase-orders', views.PurchaseOrderViewSet, basename='purchase-order')
router.register(r'goods-receipts', views.GoodsReceiptViewSet, basename='goods-receipt')
router.register(r'items', views.ItemViewSet, basename='item')
router.register(r'quotes', views.SupplierQuoteViewSet, basename='supplier-quote')
router.register(r'invoices', views.InvoiceViewSet, basename='invoice')

urlpatterns = [
    path('purchase-orders/<pk>/pdf/', views.PurchaseOrderPDFView.as_view(), name='purchase-order-pdf'),
    path('', include(router.urls)),
]