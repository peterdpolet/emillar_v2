from rest_framework import serializers
from ..models import GoodsReceipt, GoodsReceiptLine


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