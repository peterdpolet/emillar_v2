import io

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from weasyprint import HTML

from config.authentication import QueryParamJWTAuthentication
from ..models import PurchaseOrder


class PurchaseOrderPDFView(APIView):
    authentication_classes = [QueryParamJWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def get(self, request, pk):
        try:
            po = PurchaseOrder.objects.prefetch_related(
                'lines', 'lines__item'
            ).select_related('supplier', 'raised_by').get(pk=pk)
        except PurchaseOrder.DoesNotExist:
            return HttpResponse(status=404)

        html_string = render_to_string(
            'purchasing/purchase_order_pdf.html', {'po': po})
        pdf_file = io.BytesIO()
        HTML(string=html_string).write_pdf(pdf_file)
        pdf_file.seek(0)
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="PO-{po.reference}.pdf"'
        return response