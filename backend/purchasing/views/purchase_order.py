from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from ..models import PurchaseOrder, PurchaseOrderLine
from ..serializers import (
    PurchaseOrderSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderLineWriteSerializer,
    OpenSOLineSerializer,
)


class PurchaseOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['status', 'supplier']
    search_fields      = ['reference', 'supplier_ref', 'supplier__bp_name']
    ordering_fields    = ['created_at', 'expected_date', 'status']
    ordering           = ['-created_at']

    def get_queryset(self):
        return PurchaseOrder.objects.prefetch_related(
            'lines', 'lines__item', 'goods_receipts', 'sales_orders'
        ).select_related('supplier', 'raised_by').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        po = serializer.save(raised_by=self.request.user)
        if not po.reference:
            year   = timezone.now().year
            prefix = f'PO-{year}-'
            last   = PurchaseOrder.objects.filter(
                reference__startswith=prefix
            ).exclude(pk=po.pk).order_by('-reference').first()
            if last:
                try:
                    last_num = int(last.reference.split('-')[-1])
                except ValueError:
                    last_num = 0
            else:
                last_num = 0
            po.reference = f'{prefix}{str(last_num + 1).zfill(3)}'
            po.save(update_fields=['reference'])

    # ── Open SO lines for PO creation ─────────────────────────
    @action(detail=False, methods=['get'], url_path='open-so-lines')
    def open_so_lines(self, request):
        from sales.models import SalesOrderLine
        lines = SalesOrderLine.objects.filter(
            status__in=['requested', 'rfq_sent', 'quoted']
        ).select_related(
            'sales_order', 'sales_order__customer', 'supplier'
        ).order_by('sales_order__reference', 'line_number')
        return Response(OpenSOLineSerializer(lines, many=True).data)

    # ── Add a line ─────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='add-line')
    def add_line(self, request, pk=None):
        po         = self.get_object()
        serializer = PurchaseOrderLineWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(purchase_order=po)
            po.refresh_from_db()
            return Response(PurchaseOrderSerializer(po).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ── Remove a line ──────────────────────────────────────────
    @action(detail=True, methods=['delete'],
            url_path=r'remove-line/(?P<line_id>[^/.]+)')
    def remove_line(self, request, pk=None, line_id=None):
        po = self.get_object()
        try:
            line = po.lines.get(pk=line_id)
            line.delete()
            return Response(PurchaseOrderSerializer(po).data)
        except PurchaseOrderLine.DoesNotExist:
            return Response({'detail': 'Line not found.'},
                            status=status.HTTP_404_NOT_FOUND)

    # ── Mark sent ──────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='mark-sent')
    def mark_sent(self, request, pk=None):
        po = self.get_object()
        if po.status != 'draft':
            return Response(
                {'detail': 'Only draft POs can be marked as sent.'},
                status=status.HTTP_400_BAD_REQUEST)
        po.status = 'sent'
        po.save(update_fields=['status', 'updated_at'])
        return Response(PurchaseOrderSerializer(po).data)

    # ── Cancel ─────────────────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        po = self.get_object()
        if po.status in ['complete', 'cancelled']:
            return Response(
                {'detail': 'Cannot cancel a completed or cancelled PO.'},
                status=status.HTTP_400_BAD_REQUEST)
        po.status = 'cancelled'
        po.save(update_fields=['status', 'updated_at'])
        return Response(PurchaseOrderSerializer(po).data)

    # ── Update line notes ──────────────────────────────────────
    @action(detail=True, methods=['patch'],
            url_path=r'update-line-notes/(?P<line_id>[^/.]+)')
    def update_line_notes(self, request, pk=None, line_id=None):
        po = self.get_object()
        try:
            line = po.lines.get(pk=line_id)
        except PurchaseOrderLine.DoesNotExist:
            return Response({'detail': 'Line not found.'},
                            status=status.HTTP_404_NOT_FOUND)
        line.notes = request.data.get('notes', '')
        line.save(update_fields=['notes'])
        return Response(PurchaseOrderSerializer(po).data)

    # ── Recalculate totals ─────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='recalculate')
    def recalculate(self, request, pk=None):
        po = self.get_object()
        po.recalculate_totals()
        po.refresh_from_db()
        return Response(PurchaseOrderSerializer(po).data)

    # ── Link sales orders ──────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='link-sales-orders')
    def link_sales_orders(self, request, pk=None):
        po     = self.get_object()
        so_ids = request.data.get('sales_order_ids', [])
        if so_ids:
            po.sales_orders.set(so_ids)
        return Response(PurchaseOrderSerializer(po).data)