from rest_framework import serializers
from ..models import Invoice, InvoiceLine


class InvoiceLineSerializer(serializers.ModelSerializer):
    line_total     = serializers.ReadOnlyField()
    line_total_gbp = serializers.ReadOnlyField()
    po_line_detail = serializers.SerializerMethodField()
    grn_received   = serializers.SerializerMethodField()

    class Meta:
        model  = InvoiceLine
        fields = [
            'id', 'po_line', 'description', 'quantity', 'unit_price',
            'currency', 'fx_rate', 'match_status', 'match_notes',
            'line_total', 'line_total_gbp',
            'po_line_detail', 'grn_received',
        ]

    def get_po_line_detail(self, obj):
        if not obj.po_line:
            return None
        return {
            'quantity':    obj.po_line.quantity,
            'unit_price':  str(obj.po_line.unit_cost),
            'description': obj.po_line.description,
        }

    def get_grn_received(self, obj):
        if not obj.po_line:
            return None
        return sum(
            rl.quantity_received
            for grn in obj.po_line.purchase_order.goods_receipts.all()
            for rl in grn.lines.filter(po_line=obj.po_line)
        )


class InvoiceSerializer(serializers.ModelSerializer):
    lines         = InvoiceLineSerializer(many=True, read_only=True)
    total_gbp     = serializers.ReadOnlyField()
    supplier_name = serializers.SerializerMethodField()

    def get_supplier_name(self, obj):
        return obj.supplier.bp_name if obj.supplier else None

    class Meta:
        model  = Invoice
        fields = [
            'id', 'supplier_name', 'purchase_order', 'invoice_number',
            'invoice_date', 'currency', 'fx_rate', 'fx_rate_date',
            'status', 'notes', 'total_gbp', 'lines',
            'created_at', 'updated_at',
        ]