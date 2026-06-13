from django.db import models

from apps.companies.models import Company

DEFAULT_PIPELINE_STAGES = [
    "Applied",
    "Screening",
    "Interview",
    "Offer",
    "Hired",
    "Rejected",
]


class JobQuerySet(models.QuerySet):
    def for_company(self, company):
        return self.filter(company=company)

    def open(self):
        return self.filter(status=Job.Status.OPEN, company__is_active=True)


class JobManager(models.Manager.from_queryset(JobQuerySet)):
    pass


class Job(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        ARCHIVED = "archived", "Archived"

    class EmploymentType(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"
        INTERNSHIP = "internship", "Internship"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    title = models.CharField(max_length=255)
    description = models.TextField()
    department = models.CharField(max_length=128, blank=True)
    location = models.CharField(max_length=255, blank=True)
    employment_type = models.CharField(
        max_length=32,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.DRAFT)
    pipeline_stages = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = JobManager()

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} ({self.company.slug})"

    def save(self, *args, **kwargs):
        if not self.pipeline_stages:
            self.pipeline_stages = list(DEFAULT_PIPELINE_STAGES)
        super().save(*args, **kwargs)
