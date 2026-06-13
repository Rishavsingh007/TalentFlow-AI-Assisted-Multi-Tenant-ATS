from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.audit.services import log_action
from apps.jobs.models import Job


@transaction.atomic
def publish_job(job: Job, *, actor) -> Job:
    if job.status != Job.Status.DRAFT:
        raise ValidationError({"status": "Only draft jobs can be published."})

    job.status = Job.Status.OPEN
    job.save(update_fields=["status", "updated_at"])
    log_action(
        actor=actor,
        action="job.published",
        instance=job,
        metadata={"title": job.title, "status": job.status},
    )
    # Phase 9: invalidate jobs:public:list cache
    return job
