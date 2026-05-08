from django.contrib import admin
from .models import Item, PurchaseOrder, PurchaseOrderLine, GoodsReceipt, GoodsReceiptLine


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ['sku', 'name', 'status', 'carat_weight', 'base_price', 'currency']
    list_filter   = ['status', 'currency']
    search_fields = ['sku', 'name', 'certification_number']
    fieldsets = [
        ('Item', {
            'fields': ['sku', 'name', 'description', 'status']
        }),
        ('Stone details', {
            'fields': ['certification_number', 'carat_weight', 'origin']
        }),
        ('Pricing', {
            'fields': ['base_price', 'currency']
        }),
    ]


class PurchaseOrderLineInline(admin.TabularInline):
    model  = PurchaseOrderLine
    extra  = 1
    fields = ['item', 'supplier_sku', 'quantity', 'unit_cost', 'quantity_received']
    readonly_fields = ['quantity_received']
    autocomplete_fields = ['item']


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display  = ['reference', 'supplier', 'status', 'total', 'currency', 'created_at']
    list_filter   = ['status', 'currency']
    search_fields = ['reference', 'supplier_ref', 'supplier__name']
    readonly_fields = ['total', 'created_at', 'updated_at']
    inlines       = [PurchaseOrderLineInline]
    autocomplete_fields = ['supplier']

    fieldsets = [
        ('Purchase order', {
            'fields': ['supplier', 'reference', 'supplier_ref', 'status',
                      'raised_by', 'currency', 'expected_date', 'notes']
        }),
        ('Total (auto-calculated)', {
            'fields': ['total'],
            'classes': ['collapse']
        }),
        ('PDF', {
            'fields': ['po_pdf'],
            'classes': ['collapse']
        }),
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.recalculate_totals()

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        form.instance.recalculate_totals()


class GoodsReceiptLineInline(admin.TabularInline):
    model  = GoodsReceiptLine
    extra  = 1
    fields = ['po_line', 'quantity_received', 'discrepancy', 'discrepancy_note']


@admin.register(GoodsReceipt)
class GoodsReceiptAdmin(admin.ModelAdmin):
    list_display  = ['id', 'purchase_order', 'received_date', 'received_by', 'delivery_ref']
    list_filter   = ['received_date']
    search_fields = ['delivery_ref', 'purchase_order__reference']
    inlines       = [GoodsReceiptLineInline]
