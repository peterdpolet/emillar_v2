# inventory/views.py
from rest_framework import viewsets, filters, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Item, Color, Clarity, Cut
from .serializers import ItemSerializer, ColorSerializer, ClaritySerializer, CutSerializer


class ItemViewSet(viewsets.ModelViewSet):
    filter_backends = [filters.SearchFilter]
    search_fields   = ['sku', 'name']
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ItemSerializer
    ordering_fields    = ['sku', 'name', 'created_at']
    ordering           = ['sku']

    def get_queryset(self):
        return Item.objects.all()

class ColorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ColorSerializer
    queryset           = Color.objects.all()


class ClarityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ClaritySerializer
    queryset           = Clarity.objects.order_by('num_code')


class CutViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = CutSerializer
    queryset           = Cut.objects.all()