# inventory/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Item, Color, Clarity, Cut
from .serializers import ItemSerializer, ColorSerializer, ClaritySerializer, CutSerializer


class ItemViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = ItemSerializer
    search_fields      = ['sku', 'name', 'stone_detail__certification_number']
    ordering_fields    = ['sku', 'name', 'created_at']
    ordering           = ['sku']

    def get_queryset(self):
        return Item.objects.select_related(
            'stone_detail',
            'stone_detail__colour',
            'stone_detail__clarity',
            'stone_detail__cut',
        ).all()

class ColorViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = ColorSerializer
    queryset           = Color.objects.all()


class ClarityViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = ClaritySerializer
    queryset           = Clarity.objects.order_by('num_code')


class CutViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = CutSerializer
    queryset           = Cut.objects.all()