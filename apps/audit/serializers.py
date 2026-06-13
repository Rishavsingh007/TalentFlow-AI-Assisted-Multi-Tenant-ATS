from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True, allow_null=True)

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "action",
            "object_type",
            "object_id",
            "metadata",
            "actor_email",
            "timestamp",
        )
        read_only_fields = fields
