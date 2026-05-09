from django.contrib import admin
from .models import SalesOrder, SalesOrderLine, SalesOrderStatusLog


class SalesOrderLineInline(admin.TabularInline):
    model  = SalesOrderLine
    extra  = 1
    fields = ['item', 'quantity', 'unit_price']
    autocomplete_fields = ['item']


class SalesOrderStatusLogInline(admin.TabularInline):
    model       = SalesOrderStatusLog
    extra       = 0
    readonly_fields = ['from_status', 'to_status', 'note', 'changed_by', 'changed_at']
    can_delete  = False


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'customer', 'status', 'total', 'currency', 'created_at']
    list_filter   = ['status', 'currency']
    search_fields = ['customer__email', 'customer__first_name', 'customer__last_name']
    readonly_fields = ['subtotal', 'vat_amount', 'total', 'created_at', 'updated_at']
    inlines       = [SalesOrderLineInline, SalesOrderStatusLogInline]

    fieldsets = [
        ('Order', {
            'fields': ['customer', 'status', 'currency', 'notes', 'due_date']
        }),
        ('Totals', {
            'fields': ['subtotal', 'vat_amount', 'total'],
            'classes': ['collapse']
        }),
        ('PDF', {
            'fields': ['invoice_pdf'],
            'classes': ['collapse']
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.recalculate_totals()

    def save_formset(self, request, form, formset, change):
        super().save_formset(request, form, formset, change)
        form.instance.recalculate_totals()
