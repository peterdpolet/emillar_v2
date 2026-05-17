from django.shortcuts import render
from .models import BusinessPartner
from django.db.models import Max
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from partners.models import BusinessPartner
from partners.api.serializers import BusinessPartnerSerializer
from partners.api.serializers import CustomerSerializer
from partners.api.filters import BusinessPartnerFilter
from accounts.models import CustomUser

class BusinessPartnerListCreateAPIView(generics.ListCreateAPIView):
    queryset = BusinessPartner.objects.all()
    serializer_class = BusinessPartnerSerializer
    filterset_class = BusinessPartnerFilter
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['bp_name', 'bp_int_ref', 'bp_city', 'bp_country', 'bp_email']
    ordering_fields = ['bp_name', 'bp_city', 'bp_country']
    ordering        = ['bp_name']

    def get_queryset(self):
        return BusinessPartner.objects.filter(bp_type='SUPP')

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

class CustomerListCreateAPIView(generics.ListCreateAPIView):
    queryset = BusinessPartner.objects.all()
    serializer_class = CustomerSerializer