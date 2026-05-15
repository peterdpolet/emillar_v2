from rest_framework import serializers
from .models import SalesOrder, SalesOrderLine, ApprovalNote


class SalesOrderLineSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.bp_name', read_only=True)

    class Meta:
        model  = SalesOrderLine
        fields = [
            'sol_id', 'sales_order', 'line_number', 'stone_type', 'item_type', 'status',
            'supplier', 'supplier_name', 'supplier_sku',
            'inventory_item', 'quantity',
            'min_size', 'preferred_size', 'max_size',
            'min_carat', 'preferred_carat', 'max_carat',
            'colour_spec', 'clarity_spec',
            'min_price', 'max_price',
            'certificate_type', 'certificate_number',
            'agreed_price', 'notes', 'is_high_conversion',
        ]
        read_only_fields = ['sol_id', 'is_high_conversion', 'supplier_name']


class SalesOrderSerializer(serializers.ModelSerializer):
    lines          = SalesOrderLineSerializer(many=True, read_only=True)
    customer_name  = serializers.CharField(source='customer.bp_name', read_only=True)
    raised_by_name = serializers.SerializerMethodField()

    def get_raised_by_name(self, obj):
        return obj.raised_by.email if obj.raised_by else '—'

    class Meta:
        model = SalesOrder
        fields = [
            'so_id', 'reference', 'customer', 'customer_name',
            'raised_by', 'raised_by_name', 'raised_date', 'status', 'currency',
            'notes', 'customer_po_ref', 'required_by', 'delivery_address',
            'lines', 'created_at', 'updated_at',
        ]
        read_only_fields = ['so_id', 'reference', 'raised_date', 'raised_by', 'created_at', 'updated_at']


class ApprovalNoteSerializer(serializers.ModelSerializer):
    customer_name    = serializers.CharField(source='customer.bp_name', read_only=True)
    days_remaining   = serializers.IntegerField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)

    class Meta:
        model  = ApprovalNote
        fields = [
            'approval_id', 'reference', 'sales_order_line', 'customer', 'customer_name',
            'issued_by', 'issued_date', 'approval_days', 'expiry_date',
            'certificate_type', 'certificate_number',
            'agreed_price', 'currency', 'status',
            'confirmed_date', 'returned_date', 'return_type',
            'notes', 'days_remaining', 'is_expiring_soon',
        ]
        read_only_fields = ['approval_id', 'reference', 'expiry_date', 'days_remaining', 'is_expiring_soon']