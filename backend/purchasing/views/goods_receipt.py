from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import GoodsReceipt, GoodsReceiptLine
from ..serializers import (
    GoodsReceiptSerializer,
    GoodsReceiptLineWriteSerializer,
)


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
            gr.refresh_from_db()
            return Response(GoodsReceiptSerializer(gr).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # ── Update a receipt line ──────────────────────────────────
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)