from rest_framework import serializers

from .models import Application


class ApplySerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")
    resume = serializers.FileField()


class ApplicationCreatedSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField(source="job.id", read_only=True)

    class Meta:
        model = Application
        fields = ("id", "job_id", "current_stage", "applied_at")
        read_only_fields = fields
