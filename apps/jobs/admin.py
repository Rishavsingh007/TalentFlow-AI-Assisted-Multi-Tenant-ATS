from django.contrib import admin

from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "status", "employment_type", "location", "created_at")
    list_filter = ("status", "employment_type")
    search_fields = ("title", "company__name", "company__slug")
    raw_id_fields = ("company",)
