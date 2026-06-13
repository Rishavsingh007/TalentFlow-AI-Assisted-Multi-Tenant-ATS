from apps.companies.models import Company, CompanyMember
from apps.jobs.models import Job
from rest_framework.exceptions import NotFound


def get_company_for_member(*, slug: str, user) -> Company:
    try:
        company = Company.objects.get(slug=slug, is_active=True)
    except Company.DoesNotExist:
        raise NotFound()

    if not CompanyMember.objects.filter(user=user, company=company).exists():
        raise NotFound()

    return company


def get_job_for_company(*, slug: str, job_id: int, user) -> Job:
    company = get_company_for_member(slug=slug, user=user)
    try:
        return Job.objects.get(id=job_id, company=company)
    except Job.DoesNotExist:
        raise NotFound()


def get_open_job(job_id: int) -> Job:
    try:
        return Job.objects.select_related("company").get(
            id=job_id,
            status=Job.Status.OPEN,
            company__is_active=True,
        )
    except Job.DoesNotExist:
        raise NotFound()
