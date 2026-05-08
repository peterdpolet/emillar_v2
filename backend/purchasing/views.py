from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import (
    Item,
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine,
)
from .serializers import (
    ItemSerializer,
    PurchaseOrderSerializer, PurchaseOrderListSerializer,
    PurchaseOrderLineWriteSerializer,
    GoodsReceiptSerializer, GoodsReceiptLineWriteSerializer,
)

class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields      = ['sku', 'name', 'certification_number']
    ordering_fields    = ['sku', 'name', 'created_at']
    ordering           = ['sku']

    def get_queryset(self):
        return Item.objects.all()

    def get_serializer_class(self):
        return ItemSerializer

    def perform_destroy(self, instance):
        # Archive instead of hard delete
        instance.status = 'archived'
        instance.save(update_fields=['status'])



class PurchaseOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['status', 'supplier']
    search_fields      = ['reference', 'supplier_ref',
                          'supplier__name']
    ordering_fields    = ['created_at', 'expected_date', 'status']
    ordering           = ['-created_at']

    def get_queryset(self):
        return PurchaseOrder.objects.prefetch_related(
            'lines', 'lines__item', 'goods_receipts'
        ).select_related('supplier', 'raised_by').all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PurchaseOrderListSerializer
        return PurchaseOrderSerializer

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)

    # ── Add a line to an existing PO ──────────────────────────
    @action(detail=True, methods=['post'], url_path='add-line')
    def add_line(self, request, pk=None):
        po         = self.get_object()
        serializer = PurchaseOrderLineWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(purchase_order=po)
            return Response(PurchaseOrderSerializer(po).data)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

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

    # ── Mark PO as sent ───────────────────────────────────────
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

    # ── Cancel PO ─────────────────────────────────────────────
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


class GoodsReceiptViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filterset_fields   = ['purchase_order']
    ordering           = ['-received_date']

    def get_queryset(self):
        return GoodsReceipt.objects.prefetch_related(
            'lines', 'lines__po_line', 'lines__po_line__item'
        ).select_related(
            'purchase_order', 'purchase_order__supplier', 'received_by'
        ).all()

    def get_serializer_class(self):
        return GoodsReceiptSerializer

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)

    # ── Add a receipt line ────────────────────────────────────
    @action(detail=True, methods=['post'], url_path='add-line')
    def add_line(self, request, pk=None):
        gr         = self.get_object()
        serializer = GoodsReceiptLineWriteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(goods_receipt=gr)
            # Refresh from DB after save triggers _update_po_line_received
            gr.refresh_from_db()
            return Response(GoodsReceiptSerializer(gr).data)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    # ── Update a receipt line (correct a quantity) ─────────────
    @action(detail=True, methods=['patch'],
            url_path=r'update-line/(?P<line_id>[^/.]+)')
    def update_line(self, request, pk=None, line_id=None):
        gr = self.get_object()
        try:
            line = gr.lines.get(pk=line_id)
        except GoodsReceiptLine.DoesNotExist:
            return Response({'detail': 'Line not found.'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = GoodsReceiptLineWriteSerializer(
            line, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            gr.refresh_from_db()
            return Response(GoodsReceiptSerializer(gr).data)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)