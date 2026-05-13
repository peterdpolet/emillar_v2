from rest_framework import viewsets, permissions
from .models import SalesOrder, SalesOrderLine, RFQ, RFQResponse, ApprovalNote
from .serializers import (
    SalesOrderSerializer, SalesOrderLineSerializer,
    RFQSerializer, RFQResponseSerializer, ApprovalNoteSerializer
)


class SalesOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = SalesOrderSerializer

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)

    def get_queryset(self):
        qs = SalesOrder.objects.all()
        customer = self.request.query_params.get('customer')
        if customer:
            qs = qs.filter(customer__bp_id=customer)
        return qs

class SalesOrderLineViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = SalesOrderLineSerializer

    def get_queryset(self):
        qs = SalesOrderLine.objects.all()
        sales_order = self.request.query_params.get('sales_order')
        if sales_order:
            qs = qs.filter(sales_order__so_id=sales_order)
        return qs

class RFQViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = RFQSerializer
    queryset           = RFQ.objects.all()

    def perform_create(self, serializer):
        serializer.save(raised_by=self.request.user)


class RFQResponseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = RFQResponseSerializer
    queryset           = RFQResponse.objects.all()


class ApprovalNoteViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class   = ApprovalNoteSerializer
    queryset           = ApprovalNote.objects.all()
