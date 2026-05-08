from rest_framework import serializers
from .models import (
    Item,
    PurchaseOrder, PurchaseOrderLine,
    GoodsReceipt, GoodsReceiptLine,
)


# ── Item ─────────────────────────────────────────────────────

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Item
        fields = [
            'id', 'sku', 'name', 'description', 'status',
            'certification_number', 'carat_weight', 'origin',
            'base_price', 'currency',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


# ── Purchase order ───────────────────────────────────────────

class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    item_name  = serializers.CharField(source='item.name', read_only=True)
    item_sku   = serializers.CharField(source='item.sku',  read_only=True)
    line_total = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    match_status = serializers.CharField(read_only=True)
    outstanding  = serializers.IntegerField(read_only=True)

    class Meta:
        model  = PurchaseOrderLine
        fields = [
            'id', 'item', 'item_name', 'item_sku',
            'supplier_sku', 'quantity', 'unit_cost',
            'quantity_received', 'outstanding',
            'line_total', 'match_status',
        ]
        read_only_fields = ['quantity_received']


class PurchaseOrderLineWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PurchaseOrderLine
        fields = ['item', 'supplier_sku', 'quantity', 'unit_cost']


class PurchaseOrderSerializer(serializers.ModelSerializer):
    lines         = PurchaseOrderLineSerializer(many=True, read_only=True)
    supplier_name = serializers.CharField(
        source='supplier.name', read_only=True
    )
    raised_by_name = serializers.CharField(
        source='raised_by.get_full_name', read_only=True
    )
    total_expected = serializers.IntegerField(read_only=True)
    total_received = serializers.IntegerField(read_only=True)

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier_ref',
            'supplier', 'supplier_name',
            'status', 'currency', 'total',
            'raised_by', 'raised_by_name',
            'expected_date', 'notes',
            'total_expected', 'total_received',
            'po_pdf', 'lines',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'total', 'po_pdf',
            'created_at', 'updated_at',
        ]


class PurchaseOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views — no lines."""
    supplier_name = serializers.CharField(
        source='supplier.name', read_only=True
    )
    total_expected = serializers.IntegerField(read_only=True)
    total_received = serializers.IntegerField(read_only=True)

    class Meta:
        model  = PurchaseOrder
        fields = [
            'id', 'reference', 'supplier', 'supplier_name',
            'status', 'currency', 'total',
            'total_expected', 'total_received',
            'expected_date', 'created_at',
        ]


# ── Goods receipt ────────────────────────────────────────────

class GoodsReceiptLineSerializer(serializers.ModelSerializer):
    item_name    = serializers.CharField(
        source='po_line.item.name', read_only=True
    )
    item_sku     = serializers.CharField(
        source='po_line.item.sku', read_only=True
    )

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
    lines          = GoodsReceiptLineSerializer(many=True, read_only=True)
    received_by_name = serializers.CharField(
        source='received_by.get_full_name', read_only=True
    )
    po_reference   = serializers.CharField(
        source='purchase_order.reference', read_only=True
    )

    class Meta:
        model  = GoodsReceipt
        fields = [
            'id', 'purchase_order', 'po_reference',
            'delivery_ref', 'received_date', 'notes',
            'received_by', 'received_by_name',
            'lines', 'created_at',
        ]
        read_only_fields = ['created_at']