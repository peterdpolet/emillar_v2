from celery import shared_task
from django.core.files.base import ContentFile


@shared_task
def generate_and_store_invoice(order_id):
    """Generate invoice PDF and store on the Order model."""
    from sales.models import SalesOrder
    from .views import render_pdf

    order    = SalesSalesOrder.objects.get(pk=order_id)
    pdf      = render_pdf('documents/invoice.html', {'order': order})
    filename = f"invoices/invoice-{order.id}.pdf"
    order.invoice_pdf.save(filename, ContentFile(pdf), save=True)


@shared_task
def generate_and_store_po(po_id):
    """Generate PO PDF and store on the PurchaseOrder model."""
    from purchasing.models import PurchaseOrder
    from .views import render_pdf

    po       = PurchaseSalesSalesOrder.objects.get(pk=po_id)
    pdf      = render_pdf('documents/purchase_order.html', {'po': po})
    filename = f"purchase_orders/po-{po.reference}.pdf"
    po.po_pdf.save(filename, ContentFile(pdf), save=True)
