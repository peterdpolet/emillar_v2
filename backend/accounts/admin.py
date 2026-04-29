"""accounts/admin.py"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display  = ('email', 'name', 'role', 'company', 'is_active', 'totp_enabled')
    list_filter   = ('role', 'is_active', 'totp_enabled')
    search_fields = ('email', 'name', 'company')
    ordering      = ('email',)

    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        ('Personal',     {'fields': ('name', 'company', 'phone')}),
        ('Role',         {'fields': ('role',)}),
        ('2FA',          {'fields': ('totp_enabled', 'totp_secret')}),
        ('Permissions',  {'fields': ('is_active', 'is_staff', 'is_superuser',
                                     'groups', 'user_permissions')}),
        ('Timestamps',   {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields   = ('created_at', 'updated_at', 'totp_secret')
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'name', 'role', 'company',
                        'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )

    # Staff can activate/deactivate accounts from the list
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_users.short_description = 'Deactivate selected users'
