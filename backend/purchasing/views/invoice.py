from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Invoice, InvoiceLine, PurchaseOrder
from ..serializers import InvoiceSerializer, InvoiceLineSerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset           = Invoice.objects.prefetch_related(
                             'lines__po_line'
                         ).select_related('supplier', 'purchase_order')
    serializer_class   = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs          = super().get_queryset()
        po_id       = self.request.query_params.get('purchase_order')
        supplier_id = self.request.query_params.get('supplier')
        if po_id:
            qs = qs.filter(purchase_order_id=po_id)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        return qs

    def perform_create(self, serializer):
        po_id = self.request.data.get('purchase_order')
        po    = PurchaseOrder.objects.get(id=po_id)
        serializer.save(supplier=po.supplier)

    @action(detail=True, methods=['post'])
    def run_match(self, request, pk=None):
        invoice    = self.get_object()
        invoice.run_match()
        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_line(self, request, pk=None):
        invoice    = self.get_object()
        serializer = InvoiceLineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(invoice=invoice)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch'],
            url_path=r'lines/(?P<line_id>[^/.]+)')
    def update_line(self, request, pk=None, line_id=None):
        invoice = self.get_object()
        try:
            line = invoice.lines.get(pk=line_id)
        except InvoiceLine.DoesNotExist:
            return Response({'detail': 'Line not found.'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = InvoiceLineSerializer(line, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            invoice.refresh_from_db()
            return Response(InvoiceSerializer(invoice).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)