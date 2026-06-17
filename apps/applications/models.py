from django.db import models

from apps.candidates.models import Candidate
from apps.companies.models import Company
from apps.jobs.models import Job


class Application(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"
        HIRED = "hired", "Hired"

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="applications")
    applicant_full_name = models.CharField(max_length=255)
    applicant_email = models.EmailField()
    applicant_phone = models.CharField(max_length=32, blank=True)
    resume_file = models.FileField(upload_to="applications/%Y/%m/")
    parsed_resume_text = models.TextField(blank=True)
    current_stage = models.CharField(max_length=64, default="Applied")
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    ai_score = models.FloatField(null=True, blank=True)
    ai_summary = models.TextField(blank=True)
    ai_scored_at = models.DateTimeField(null=True, blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-applied_at"]
        unique_together = [("job", "candidate")]

    def __str__(self):
        return f"{self.applicant_email} → {self.job.title}"
