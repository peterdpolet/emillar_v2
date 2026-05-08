from django.db import transaction
from rest_framework import serializers
from partners.models import BusinessPartner


class BusinessPartnerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPartner
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = BusinessPartner
        fields = ('bp_id', 'bp_name', 'bp_type')

