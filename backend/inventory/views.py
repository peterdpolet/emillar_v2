# inventory/views.py
from rest_framework import viewsets, filters, permissions
from rest_framework.permissions import IsAuthenticated
from .models import Item, Color, Clarity, Cut, StockMovement
from .serializers import ItemSerializer, ColorSerializer, ClaritySerializer, CutSerializer, StockMovementSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db.models import Exists, OuterRef

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


class StockMovementViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = StockMovementSerializer
    filterset_fields   = ['transaction_type', 'supplier', 'customer', 'item']
    ordering           = ['-date', '-created_at']

    def get_queryset(self):
        return StockMovement.objects.select_related(
            'item', 'supplier', 'customer',
            'purchase_order', 'customer_memo', 'created_by'
        ).all()

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        if instance.transaction_type == 'appro_in' and not instance.appro_reference:
            instance.appro_reference = StockMovement.generate_appro_reference()
            instance.save(update_fields=['appro_reference'])

    @action(detail=False, methods=['get'], url_path='open-appro-refs')
    def open_appro_refs(self, request):
        from django.db.models import Exists, OuterRef
        refs = StockMovement.objects.filter(
            transaction_type='appro_in',
            appro_reference__gt=''
        ).exclude(
            Exists(
                StockMovement.objects.filter(
                    appro_reference=OuterRef('appro_reference'),
                    transaction_type__in=['appro_return_out', 'purchased']
                )
            )
        ).values_list('appro_reference', flat=True).distinct()
        return Response(list(refs))

    @action(detail=False, methods=['get'], url_path='appro-summary')
    def appro_summary(self, request):
        from django.db.models import Exists, OuterRef, Q

        resolved_out = StockMovement.objects.filter(
            Q(appro_reference=OuterRef('appro_reference'), appro_reference__gt='') |
            Q(appro_reference='', item=OuterRef('item'), item__isnull=False) |
            Q(appro_reference='', item__isnull=True, parcel_description=OuterRef('parcel_description')),
            transaction_type__in=['appro_return_out', 'purchased']
        )
        appro_in = StockMovement.objects.filter(
            transaction_type='appro_in'
        ).exclude(
            Exists(resolved_out)
        ).select_related('item', 'supplier', 'purchase_order')

        resolved_in = StockMovement.objects.filter(
            Q(appro_reference=OuterRef('appro_reference'), appro_reference__gt='') |
            Q(appro_reference='', item=OuterRef('item'), item__isnull=False) |
            Q(appro_reference='', item__isnull=True, parcel_description=OuterRef('parcel_description')),
            transaction_type__in=['appro_return_in', 'sold']
        )
        appro_out = StockMovement.objects.filter(
            transaction_type='appro_out'
        ).exclude(
            Exists(resolved_in)
        ).select_related('item', 'customer', 'customer_memo')

        return Response({
            'appro_in':  StockMovementSerializer(appro_in,  many=True).data,
            'appro_out': StockMovementSerializer(appro_out, many=True).data,
        })