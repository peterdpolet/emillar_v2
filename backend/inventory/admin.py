from django.contrib import admin
from .models import Item, GemDetail, Color, Clarity, Cut


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ['sku', 'name', 'status', 'base_price', 'currency']
    list_filter   = ['status', 'currency']
    search_fields = ['sku', 'name']    # ← required for autocomplete
    fieldsets = [
        ('Item', {
            'fields': ['sku', 'name', 'description', 'status']
        }),
        ('Pricing', {
            'fields': ['base_price', 'currency'],
        }),
    ]


@admin.register(GemDetail)
class GemDetailAdmin(admin.ModelAdmin):
    list_display  = ['item', 'certification_number', 'carat_weight', 'color', 'clarity', 'cut']
    search_fields = ['item__sku', 'item__name', 'certification_number']


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display  = ['code', 'desc']
    search_fields = ['code', 'desc']


@admin.register(Clarity)
class ClarityAdmin(admin.ModelAdmin):
    list_display  = ['code', 'num_code', 'desc']
    search_fields = ['code', 'desc']


@admin.register(Cut)
class CutAdmin(admin.ModelAdmin):
    list_display  = ['code', 'desc']
    search_fields = ['code', 'desc']