# documents/views.py
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration

from sales.models import SalesOrder
from purchasing.models import PurchaseOrder


def render_pdf(template_name, context):
    html_string = render_to_string(template_name, context)
    font_config  = FontConfiguration()
    html         = HTML(string=html_string, base_url='/')
    return html.write_pdf(font_config=font_config)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def invoice_pdf(request, order_id):
    order = get_object_or_404(SalesOrder, pk=order_id)
    if not request.user.is_staff and order.customer != request.user:
        return HttpResponse(status=403)
    pdf      = render_pdf('documents/invoice.html', {'order': order})
    filename = f"invoice-{order.id}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    disposition = 'attachment' if request.GET.get('download') else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def purchase_order_pdf(request, po_id):
    po = get_object_or_404(PurchaseOrder, pk=po_id)
    if not request.user.is_staff:
        return HttpResponse(status=403)
    pdf      = render_pdf('documents/purchase_order.html', {'po': po})
    filename = f"purchase-order-{po.reference}.pdf"
    response = HttpResponse(pdf, content_type='application/pdf')
    disposition = 'attachment' if request.GET.get('download') else 'inline'
    response['Content-Disposition'] = f'{disposition}; filename="{filename}"'
    return response
