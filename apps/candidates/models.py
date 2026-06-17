from django.db import models

from apps.companies.models import Company


class Candidate(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="candidates")
    email = models.EmailField(db_index=True)
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["company", "email"],
                name="uniq_candidate_per_company_email",
            ),
        ]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"
