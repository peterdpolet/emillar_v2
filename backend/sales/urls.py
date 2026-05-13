from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders',        views.SalesOrderViewSet,    basename='sales-order')
router.register(r'lines',         views.SalesOrderLineViewSet, basename='sales-line')
router.register(r'rfqs',          views.RFQViewSet,           basename='rfq')
router.register(r'rfq-responses', views.RFQResponseViewSet,   basename='rfq-response')
router.register(r'approval-notes', views.ApprovalNoteViewSet, basename='approval-note')

urlpatterns = [
    path('', include(router.urls)),
]