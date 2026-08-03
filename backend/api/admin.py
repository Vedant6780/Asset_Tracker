from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Asset, AuditLog

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'role', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('role',)}),
    )

class AssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'serial_number', 'status', 'location', 'updated_at')
    search_fields = ('name', 'serial_number')
    list_filter = ('status', 'location')

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('asset', 'action', 'old_status', 'new_status', 'changed_by', 'changed_at')
    search_fields = ('asset__name', 'changed_by')
    list_filter = ('action', 'changed_at')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Asset, AssetAdmin)
admin.site.register(AuditLog, AuditLogAdmin)
