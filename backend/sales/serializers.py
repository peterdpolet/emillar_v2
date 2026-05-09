from rest_framework import serializers
from .models import SalesOrder, SalesOrderLine, SalesOrderStatusLog


class SalesOrderLineSerializer(serializers.ModelSerializer):
    item_name  = serializers.CharField(source='item.name', read_only=True)
    item_sku   = serializers.CharField(source='item.sku',  read_only=True)
    line_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model  = SalesOrderLine
        fields = [
            'id', 'item', 'item_name', 'item_sku',
            'quantity', 'unit_price', 'line_total',
        ]


class SalesOrderLineWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SalesOrderLine
        fields = ['item', 'quantity', 'unit_price']


class SalesOrderStatusLogSerializer(serializers.ModelSerializer):
    changed_by_name = serializers.CharField(
        source='changed_by.get_full_name', read_only=True
    )

    class Meta:
        model  = SalesOrderStatusLog
        fields = [
            'id', 'from_status', 'to_status',
            'note', 'changed_by', 'changed_by_name', 'changed_at'
        ]
        read_only_fields = ['changed_at']


class SalesOrderSerializer(serializers.ModelSerializer):
    lines           = SalesOrderLineSerializer(many=True, read_only=True)
    status_logs     = SalesOrderStatusLogSerializer(many=True, read_only=True)
    customer_name   = serializers.CharField(
        source='customer.get_full_name', read_only=True
    )
    customer_email  = serializers.EmailField(
        source='customer.email', read_only=True
    )

    class Meta:
        model  = SalesOrder
        fields = [
            'id', 'customer', 'customer_name', 'customer_email',
            'status', 'currency',
            'subtotal', 'vat_amount', 'total',
            'notes', 'due_date', 'invoice_pdf',
            'lines', 'status_logs',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'subtotal', 'vat_amount', 'total',
            'invoice_pdf', 'created_at', 'updated_at',
        ]


class SalesOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — no lines."""
    customer_name  = serializers.CharField(
        source='customer.get_full_name', read_only=True
    )
    customer_email = serializers.EmailField(
        source='customer.email', read_only=True
    )
    line_count = serializers.IntegerField(
        source='lines.count', read_only=True
    )

    class Meta:
        model  = SalesOrder
        fields = [
            'id', 'customer', 'customer_name', 'customer_email',
            'status', 'currency', 'total',
            'line_count', 'due_date', 'created_at',
        ]