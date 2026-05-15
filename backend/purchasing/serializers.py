# purchasing/serializers.py
from rest_framework import serializers
from .models import (
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine,
)
from .models import PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine, SupplierQuote


# ── Purchase Order Line ───────────────────────────────────────

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


# ── Purchase Order ────────────────────────────────────────────

class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines          = PurchaseOrderLineSerializer(many=True, read_only=True)
    supplier_name  = serializers.CharField(source='supplier.bp_name', read_only=True)
    raised_by_name = serializers.SerializerMethodField()
    so_reference   = serializers.CharField(source='sales_order.reference', read_only=True, default=None)

    def get_raised_by_name(self, obj):
        if not obj.raised_by:
            return None
        return obj.raised_by.email

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier_ref',
            'supplier', 'supplier_name',
            'sales_order', 'so_reference',
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
    """Lightweight — no lines, for list/accordion view."""
    supplier_name = serializers.CharField(source='supplier.bp_name', read_only=True)
    so_reference  = serializers.CharField(source='sales_order.reference', read_only=True, default=None)

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier_ref',
            'supplier', 'supplier_name',
            'sales_order', 'so_reference',
            'status', 'currency', 'total', 'total_gbp',
            'expected_date', 'raised_date', 'created_at',
        ]


# ── Goods Receipt ─────────────────────────────────────────────

class GoodsReceiptLineSerializer(serializers.ModelSerializer):
    item_name = serializers.SerializerMethodField()
    item_sku  = serializers.SerializerMethodField()

    def get_item_name(self, obj):
        if obj.po_line.item:
            return obj.po_line.item.name
        return obj.po_line.description

    def get_item_sku(self, obj):
        if obj.po_line.item:
            return obj.po_line.item.sku
        return obj.po_line.supplier_sku

    class Meta:
        model  = GoodsReceiptLine
        fields = [
            'id', 'po_line', 'item_name', 'item_sku',
            'quantity_received', 'discrepancy', 'discrepancy_note',
        ]


class GoodsReceiptLineWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = GoodsReceiptLine
        fields = ['po_line', 'quantity_received', 'discrepancy', 'discrepancy_note']


class GoodsReceiptSerializer(serializers.ModelSerializer):
    lines            = GoodsReceiptLineSerializer(many=True, read_only=True)
    received_by_name = serializers.SerializerMethodField()
    po_reference     = serializers.CharField(source='purchase_order.reference', read_only=True)

    def get_received_by_name(self, obj):
        if not obj.received_by:
            return None
        return obj.received_by.email

    class Meta:
        model  = GoodsReceipt
        fields = [
            'id', 'purchase_order', 'po_reference',
            'delivery_ref', 'supplier_ref',
            'received_by', 'received_by_name',
            'received_date', 'notes',
            'lines', 'created_at',
        ]
        read_only_fields = ['created_at']


class SupplierQuoteSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.bp_name', read_only=True)
    so_line_display = serializers.SerializerMethodField()

    class Meta:
        model = SupplierQuote
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