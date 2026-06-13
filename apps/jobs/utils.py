from apps.companies.access import get_company_for_member, get_job_for_company  # noqa: F401
from apps.jobs.models import Job
from rest_framework.exceptions import NotFound


def get_open_job(job_id: int) -> Job:
    try:
        return Job.objects.select_related("company").get(
            id=job_id,
            status=Job.Status.OPEN,
            company__is_active=True,
        )
    except Job.DoesNotExist:
        raise NotFound()
