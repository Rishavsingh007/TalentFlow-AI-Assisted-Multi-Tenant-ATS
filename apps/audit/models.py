from django.conf import settings
from django.db import models


class AuditLog(models.Model):
    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="audit_logs",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_actions",
    )
    action = models.CharField(max_length=128)
    object_type = models.CharField(max_length=64)
    object_id = models.PositiveIntegerField()
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["company", "-timestamp"]),
        ]

    def __str__(self):
        return f"{self.action} on {self.object_type}:{self.object_id}"
