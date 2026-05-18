from rest_framework import serializers
from ..models import PurchaseOrder, PurchaseOrderLine


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    item_name      = serializers.CharField(source='item.name', read_only=True, default=None)
    item_sku       = serializers.CharField(source='item.sku',  read_only=True, default=None)
    line_total     = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    line_total_gbp = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    match_status   = serializers.CharField(read_only=True)
    outstanding    = serializers.IntegerField(read_only=True)

    class Meta:
        model  = PurchaseOrderLine
        fields = [
            'id', 'purchase_order',
            'item', 'item_name', 'item_sku',
            'description', 'supplier_sku',
            'quantity', 'quantity_received', 'outstanding',
            'unit_cost', 'currency',
            'fx_rate', 'fx_rate_date', 'unit_cost_gbp',
            'line_total', 'line_total_gbp',
            'match_status', 'notes',
        ]
        read_only_fields = ['quantity_received', 'unit_cost_gbp']


class PurchaseOrderLineWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PurchaseOrderLine
        fields = [
            'item', 'description', 'supplier_sku',
            'quantity', 'unit_cost', 'currency',
            'fx_rate', 'fx_rate_date',
            'notes',
        ]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines          = PurchaseOrderLineSerializer(many=True, read_only=True)
    supplier_name  = serializers.CharField(source='supplier.bp_name', read_only=True)
    raised_by_name = serializers.SerializerMethodField()
    sales_orders   = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    so_references  = serializers.SerializerMethodField()

    def get_raised_by_name(self, obj):
        if not obj.raised_by:
            return None
        return obj.raised_by.email

    def get_so_references(self, obj):
        return [so.reference for so in obj.sales_orders.all()]

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier_ref',
            'supplier', 'supplier_name',
            'sales_orders', 'so_references',
            'status', 'raised_by', 'raised_by_name', 'raised_date',
            'currency', 'fx_rate', 'fx_rate_date',
            'total', 'total_gbp',
            'expected_date', 'notes',
            'po_pdf', 'lines',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'raised_date', 'total', 'total_gbp',
            'po_pdf', 'created_at', 'updated_at',
        ]


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.bp_name', read_only=True)
    so_references = serializers.SerializerMethodField()

    def get_so_references(self, obj):
        return [so.reference for so in obj.sales_orders.all()]

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier_ref',
            'supplier', 'supplier_name',
            'sales_orders', 'so_references',
            'status', 'currency', 'total', 'total_gbp',
            'expected_date', 'raised_date', 'created_at',
        ]