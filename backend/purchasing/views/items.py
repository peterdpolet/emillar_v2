from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from inventory.models import Item
from inventory.serializers import ItemSerializer
from ..models import PurchaseOrder


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    search_fields      = ['sku', 'name', 'certification_number']
    ordering_fields    = ['sku', 'name', 'created_at']
    ordering           = ['sku']

    def get_queryset(self):
        return Item.objects.all()

    def get_serializer_class(self):
        return ItemSerializer

    def perform_create(self, serializer):
        po_id = self.request.data.get('purchase_order')
        po = PurchaseOrder.objects.get(id=po_id)
        serializer.save(supplier=po.supplier)

    def perform_destroy(self, instance):
        instance.status = 'archived'
        instance.save(update_fields=['status'])