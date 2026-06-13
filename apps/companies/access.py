from apps.applications.models import Application
from apps.companies.models import Company, CompanyMember
from apps.jobs.models import Job
from rest_framework.exceptions import NotFound, PermissionDenied


def get_company_membership(*, slug: str, user) -> CompanyMember:
    try:
        company = Company.objects.get(slug=slug, is_active=True)
    except Company.DoesNotExist:
        raise NotFound()

    membership = CompanyMember.objects.filter(user=user, company=company).first()
    if not membership:
        raise NotFound()

    return membership


def get_company_for_member(*, slug: str, user) -> Company:
    return get_company_membership(slug=slug, user=user).company


def require_recruiter_or_admin(membership: CompanyMember) -> None:
    if membership.role not in (CompanyMember.Role.ADMIN, CompanyMember.Role.RECRUITER):
        raise PermissionDenied()


def get_job_for_company(*, slug: str, job_id: int, user) -> Job:
    company = get_company_for_member(slug=slug, user=user)
    try:
        return Job.objects.get(id=job_id, company=company)
    except Job.DoesNotExist:
        raise NotFound()


def get_application_for_company(*, slug: str, application_id: int, user) -> Application:
    company = get_company_for_member(slug=slug, user=user)
    try:
        return Application.objects.select_related("candidate", "job").get(
            id=application_id,
            company=company,
        )
    except Application.DoesNotExist:
        raise NotFound()
