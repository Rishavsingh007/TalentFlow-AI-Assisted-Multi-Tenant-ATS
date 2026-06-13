from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "job", "company", "current_stage", "status", "applied_at")
    list_filter = ("status", "current_stage")
    search_fields = ("candidate__email", "candidate__full_name", "job__title")
    raw_id_fields = ("job", "candidate", "company")
