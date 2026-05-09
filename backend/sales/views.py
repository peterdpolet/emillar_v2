from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import SalesOrder
from .serializers import SalesOrderSerializer


class SalesOrderViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class   = SalesOrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return SalesOrder.objects.all()
        return SalesOrder.objects.filter(customer=self.request.user)