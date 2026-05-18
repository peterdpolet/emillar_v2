from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import SupplierQuote
from ..serializers import SupplierQuoteSerializer


class SupplierQuoteViewSet(viewsets.ModelViewSet):
    serializer_class   = SupplierQuoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = SupplierQuote.objects.select_related(
            'supplier', 'so_line', 'so_line__sales_order'
        )
        so_line  = self.request.query_params.get('so_line')
        supplier = self.request.query_params.get('supplier')
        if so_line:
            qs = qs.filter(so_line=so_line)
        if supplier:
            qs = qs.filter(supplier=supplier)
        return qs

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        quote = self.get_object()
        if quote.status != 'received':
            return Response(
                {'detail': 'Only received quotes can be accepted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        quote.accept()
        return Response(SupplierQuoteSerializer(quote).data)