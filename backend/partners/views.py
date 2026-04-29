from django.shortcuts import render

# Create your views here.
rom .models import Supplier
from .serializers import SupplierSerializer, SupplierRefSerializer


class SupplierViewSet(viewsets.ModelViewSet):
    serializer_class   = SupplierSerializer
    permission_classes = [IsAuthenticated]
    search_fields      = ['name', 'contact_name', 'email']
    ordering_fields    = ['name', 'created_at']
    ordering           = ['name']

    def get_queryset(self):
        return Supplier.objects.all()