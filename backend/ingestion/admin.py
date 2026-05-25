from django.contrib import admin
from .models import Tenant, IngestionSource, EmissionRow, EmissionRowAudit

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')

@admin.register(IngestionSource)
class IngestionSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_type', 'tenant', 'origin_file_name', 'uploaded_at')
    list_filter = ('source_type', 'tenant')

@admin.register(EmissionRow)
class EmissionRowAdmin(admin.ModelAdmin):
    list_display = ('source_category', 'scope', 'activity_date', 'status', 'tenant')
    list_filter = ('status', 'scope', 'tenant')
    search_fields = ('activity_description', 'source_row_id')

@admin.register(EmissionRowAudit)
class EmissionRowAuditAdmin(admin.ModelAdmin):
    list_display = ('emission_row', 'change_type', 'changed_by', 'changed_at')

from .models import EmissionFactor

@admin.register(EmissionFactor)
class EmissionFactorAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'key', 'factor', 'effective_date', 'created_at')
    list_filter = ('tenant', 'key')
