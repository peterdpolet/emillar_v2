import django_filters
from inventory.models import Item

class ItemFilter(django_filters.FilterSet):

    class Meta:
        model = Item
        fields = {
            'sku':['exact'],
            'status': ['exact'],
            'supplier': ['exact']
        }

