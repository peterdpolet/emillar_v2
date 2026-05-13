from rest_framework import serializers
from .models import SalesOrder, SalesOrderLine, RFQ, RFQResponse, ApprovalNote


class SalesOrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SalesOrderLine
        fields = [
            'sol_id', 'sales_order', 'line_number', 'stone_type', 'item_type', 'status',
            'inventory_item', 'quantity',
            'min_size', 'preferred_size', 'max_size',
            'min_carat', 'preferred_carat', 'max_carat',
            'colour_spec', 'clarity_spec',
            'min_price', 'max_price',
            'certificate_type', 'certificate_number',
            'agreed_price', 'notes', 'is_high_conversion',
        ]
        read_only_fields = ['sol_id', 'is_high_conversion']


class SalesOrderSerializer(serializers.ModelSerializer):
    lines        = SalesOrderLineSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.bp_name', read_only=True)

    class Meta:
        model  = SalesOrder
        fields = [
            'so_id', 'reference', 'customer', 'customer_name',
            'raised_by', 'raised_date', 'status', 'currency',
            'notes', 'lines', 'created_at', 'updated_at',
        ]
        read_only_fields = ['so_id', 'reference', 'raised_date', 'raised_by', 'created_at', 'updated_at']


class RFQResponseSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.bp_name', read_only=True)

    class Meta:
        model  = RFQResponse
        fields = [
            'rfqr_id', 'rfq', 'supplier', 'supplier_name',
            'offered_price', 'currency', 'stone_description',
            'carat_weight', 'size_mm',
            'certificate_type', 'certificate_number',
            'response_date', 'status',
            'accepted_by', 'accepted_date', 'notes',
        ]
        read_only_fields = ['rfqr_id', 'accepted_by', 'accepted_date']


class RFQSerializer(serializers.ModelSerializer):
    responses = RFQResponseSerializer(many=True, read_only=True)

    class Meta:
        model  = RFQ
        fields = [
            'rfq_id', 'reference', 'sales_order_line',
            'raised_by', 'raised_date', 'status', 'notes', 'responses',
        ]
        read_only_fields = ['rfq_id', 'reference', 'raised_date']


class ApprovalNoteSerializer(serializers.ModelSerializer):
    customer_name  = serializers.CharField(source='customer.bp_name', read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)
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