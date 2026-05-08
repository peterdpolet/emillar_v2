from django.contrib import admin
from .models import Supplier, BusinessPartner


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display  = ['name', 'contact_name', 'email', 'phone', 'is_active']
    list_filter   = ['is_active']
    search_fields = ['name', 'contact_name', 'email']
    fieldsets = [
        ('Supplier', {
            'fields': ['name', 'contact_name', 'email', 'phone', 'is_active']
        }),
        ('Address & notes', {
            'fields': ['address', 'notes'],
            'classes': ['collapse']
        }),
    ]


@admin.register(BusinessPartner)
class BusinessPartnerAdmin(admin.ModelAdmin):
    list_display  = ['bp_name', 'bp_type', 'bp_int_ref', 'bp_email', 'bp_city', 'bp_country']
    list_filter   = ['bp_type', 'bp_country']
    search_fields = ['bp_name', 'bp_int_ref', 'bp_email', 'bp_alias_1', 'bp_alias_2']
    fieldsets = [
        ('Identity', {
            'fields': ['bp_type', 'bp_int_ref', 'bp_name', 'bp_desc',
                      'bp_alias_1', 'bp_alias_2', 'bp_comp_name']
        }),
        ('Address', {
            'fields': ['bp_addr_1', 'bp_addr_2', 'bp_addr_3', 'bp_addr_4',
                      'bp_city', 'bp_county', 'bp_country', 'bp_pcode'],
            'classes': ['collapse']
        }),
        ('Contact', {
            'fields': ['bp_email', 'bp_tel', 'bp_mob', 'bp_fax',
                      'bp_whatsapp', 'bp_fbook'],
            'classes': ['collapse']
        }),
    ]
