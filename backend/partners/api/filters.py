import django_filters
from partners.models import BusinessPartner

class BusinessPartnerFilter(django_filters.FilterSet):

    class Meta:
        model = BusinessPartner
        fields = {
            'bp_name':['iexact', 'icontains'],
            'bp_int_ref': ['exact', 'contains']
        }

