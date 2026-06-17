from django.contrib import admin

from .models import Candidate


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "company", "phone", "created_at")
    list_filter = ("company",)
    search_fields = ("full_name", "email")
