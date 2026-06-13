from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.jobs.models import Job


@transaction.atomic
def publish_job(job: Job, *, actor) -> Job:
    if job.status != Job.Status.DRAFT:
        raise ValidationError({"status": "Only draft jobs can be published."})

    job.status = Job.Status.OPEN
    job.save(update_fields=["status", "updated_at"])
    # Phase 4: audit.log_action(actor, "job.published", job, ...)
    # Phase 9: invalidate jobs:public:list cache
    return job
