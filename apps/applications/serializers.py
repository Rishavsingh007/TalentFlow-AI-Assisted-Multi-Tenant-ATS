from rest_framework import serializers

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


class ApplicantSnapshotSerializer(serializers.Serializer):
    full_name = serializers.CharField(source="applicant_full_name", read_only=True)
    email = serializers.EmailField(source="applicant_email", read_only=True)
    phone = serializers.CharField(source="applicant_phone", read_only=True)


class JobSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ("id", "title")


class ApplicationListSerializer(serializers.ModelSerializer):
    candidate = ApplicantSnapshotSerializer(source="*", read_only=True)
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


class ApplicationScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ("ai_score", "ai_summary", "ai_scored_at")
        read_only_fields = fields


class ApplicationScoreQueuedSerializer(serializers.Serializer):
    status = serializers.CharField(read_only=True)
    application_id = serializers.IntegerField(read_only=True)
