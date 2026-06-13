from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "object_type", "object_id", "company", "actor", "timestamp")
    list_filter = ("action", "object_type", "company")
    search_fields = ("action", "object_type", "actor__email", "company__name")
    readonly_fields = (
        "company",
        "actor",
        "action",
        "object_type",
        "object_id",
        "metadata",
        "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
