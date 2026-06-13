from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "description",
            "department",
            "location",
            "employment_type",
            "status",
            "pipeline_stages",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "status", "pipeline_stages", "created_at", "updated_at")


class JobCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = (
            "title",
            "description",
            "department",
            "location",
            "employment_type",
        )


class PublicJobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    company_slug = serializers.CharField(source="company.slug", read_only=True)

    class Meta:
        model = Job
        fields = (
            "id",
            "title",
            "description",
            "department",
            "location",
            "employment_type",
            "company_name",
            "company_slug",
            "created_at",
        )
        read_only_fields = fields
