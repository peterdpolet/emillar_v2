# documents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('invoices/<int:order_id>/pdf/',    views.invoice_pdf,        name='invoice-pdf'),
    path('purchase-orders/<uuid:po_id>/pdf/', views.purchase_order_pdf, name='po-pdf'),
]