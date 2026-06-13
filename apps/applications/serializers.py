from rest_framework import serializers

from apps.candidates.models import Candidate
from apps.jobs.models import Job

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


class CandidateSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ("full_name", "email", "phone")


class JobSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ("id", "title")


class ApplicationListSerializer(serializers.ModelSerializer):
    candidate = CandidateSummarySerializer(read_only=True)
    job = JobSummarySerializer(read_only=True)

    class Meta:
        model = Application
        fields = (
            "id",
            "candidate",
            "job",
            "current_stage",
            "status",
            "ai_score",
            "applied_at",
        )
        read_only_fields = fields


class ApplicationDetailSerializer(ApplicationListSerializer):
    pipeline_stages = serializers.ListField(source="job.pipeline_stages", read_only=True)

    class Meta(ApplicationListSerializer.Meta):
        fields = ApplicationListSerializer.Meta.fields + ("ai_summary", "pipeline_stages")


class StageMoveSerializer(serializers.Serializer):
    current_stage = serializers.CharField(max_length=64)
