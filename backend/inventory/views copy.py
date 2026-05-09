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

from .models import Item, GemDetail
from .serializers import ItemSerializer
from .filters import ItemFilter

from accounts.models import CustomUser

class ItemListCreateAPIView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    # queryset=queryset.filter(order_id = 'e0fd292f-988e-4303-b833-30084cb0966d')
    serializer_class = ItemSerializer
    filterset_class = ItemFilter


    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method == 'POST':
            self.permission_classes = [AllowAny]
        return super().get_permissions()

