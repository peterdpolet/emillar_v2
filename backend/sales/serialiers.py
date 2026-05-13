from rest_framework import serializers
from .models import SalesOrder, SalesOrderLine, RFQ, RFQResponse, ApprovalNote


class SalesOrderLineSerializer(serializers.ModelSerializer):
    line_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model  = OrderLine
        fields = [
            'id', 'item', 'quantity',
            'unit_price', 'line_total'
        ]


class SalesOrderSerializer(serializers.ModelSerializer):
    lines        = SalesOrderLineSerializer(many=True, read_only=True)
    customer_name  = serializers.CharField(
        source='customer.get_full_name', read_only=True
    )
    customer_email = serializers.EmailField(
        source='customer.email', read_only=True
    )

    class Meta:
        model  = SalesOrder
        fields = [
            'id', 'customer', 'customer_name', 'customer_email',
            'status', 'subtotal', 'vat_amount', 'total',
            'currency', 'notes', 'due_date',
            'invoice_pdf', 'lines',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'subtotal', 'vat_amount', 'total', 'invoice_pdf',
            'created_at', 'updated_at',
        ]