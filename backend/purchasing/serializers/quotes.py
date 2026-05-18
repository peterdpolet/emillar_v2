from rest_framework import serializers
from ..models import SupplierQuote


class SupplierQuoteSerializer(serializers.ModelSerializer):
    supplier_name   = serializers.CharField(source='supplier.bp_name', read_only=True)
    so_line_display = serializers.SerializerMethodField()

    class Meta:
        model  = SupplierQuote
        fields = [
            'id', 'so_line', 'so_line_display',
            'supplier', 'supplier_name',
            'status',
            'price', 'currency', 'fx_rate', 'fx_rate_date', 'price_gbp',
            'supplier_sku', 'valid_until', 'notes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'price_gbp', 'created_at', 'updated_at']

    def get_so_line_display(self, obj):
        line = obj.so_line
        return f'{line.sales_order.reference} — Line {line.line_number} ({line.stone_type})'