from rest_framework import serializers
from sales.models import SalesOrderLine


class OpenSOLineSerializer(serializers.ModelSerializer):
    so_reference  = serializers.CharField(source='sales_order.reference', read_only=True)
    customer_name = serializers.CharField(source='sales_order.customer.bp_name', read_only=True)
    supplier_name = serializers.CharField(source='supplier.bp_name', read_only=True, default=None)

    class Meta:
        model  = SalesOrderLine
        fields = [
            'sol_id', 'sales_order', 'so_reference', 'customer_name',
            'line_number', 'stone_type', 'item_type', 'status',
            'supplier', 'supplier_name', 'supplier_sku',
            'quantity',
            'min_carat', 'preferred_carat', 'max_carat',
            'min_size', 'preferred_size', 'max_size',
            'colour_spec', 'clarity_spec',
            'min_price', 'max_price',
            'certificate_type', 'certificate_number',
            'notes',
        ]