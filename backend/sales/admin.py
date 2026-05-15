from django.contrib import admin
from .models import SalesOrder, SalesOrderLine, ApprovalNote


class SalesOrderLineInline(admin.TabularInline):
    model  = SalesOrderLine
    extra  = 1
    fields = ['line_number', 'stone_type', 'item_type', 'status',
              'supplier', 'supplier_sku',
              'min_carat', 'preferred_carat', 'max_carat',
              'colour_spec', 'clarity_spec', 'min_price', 'max_price']


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display    = ['reference', 'customer', 'status', 'currency', 'raised_date']
    list_filter     = ['status', 'currency']
    search_fields   = ['reference', 'customer__bp_name']
    readonly_fields = ['so_id', 'reference', 'raised_date', 'created_at', 'updated_at']
    inlines         = [SalesOrderLineInline]
    fieldsets = [
        ('Order', {
            'fields': ['so_id', 'reference', 'customer', 'raised_by', 'status', 'currency', 'notes']
        }),
        ('Timestamps', {
            'fields': ['raised_date', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]


@admin.register(ApprovalNote)
class ApprovalNoteAdmin(admin.ModelAdmin):
    list_display    = ['reference', 'customer', 'status', 'issued_date',
                       'expiry_date', 'approval_days', 'agreed_price']
    list_filter     = ['status', 'approval_days', 'certificate_type']
    search_fields   = ['reference', 'customer__bp_name', 'certificate_number']
    readonly_fields = ['approval_id', 'reference', 'expiry_date']
    fieldsets = [
        ('Approval Note', {
            'fields': ['approval_id', 'reference', 'sales_order_line', 'customer',
                       'issued_by', 'issued_date', 'approval_days', 'expiry_date']
        }),
        ('Stone Details', {
            'fields': ['certificate_type', 'certificate_number', 'agreed_price', 'currency']
        }),
        ('Status', {
            'fields': ['status', 'confirmed_date', 'returned_date', 'return_type']
        }),
        ('Notes', {
            'fields': ['notes'],
            'classes': ['collapse']
        }),
    ]