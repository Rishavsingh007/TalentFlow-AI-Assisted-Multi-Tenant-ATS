import pytest

from apps.companies.models import CompanyMember
from apps.jobs.models import Job
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory


def _auth(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
def test_hiring_manager_can_list_applications(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.HIRING_MANAGER)
    ApplicationFactory(company=membership.company)
    _auth(api_client, membership)

    response = api_client.get("/api/v1/companies/acme/applications/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_manager_cannot_move_stage(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.HIRING_MANAGER)
    application = ApplicationFactory(company=membership.company, current_stage="Screening")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Interview"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_recruiter_can_move_stage(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.RECRUITER)
    application = ApplicationFactory(company=membership.company, current_stage="Applied")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Screening"},
        format="json",
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_manager_cannot_create_job(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.HIRING_MANAGER)
    _auth(api_client, membership)

    response = api_client.post(
        "/api/v1/companies/acme/jobs/",
        {
            "title": "Blocked Role",
            "description": "Should not create",
            "employment_type": "full_time",
        },
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_hiring_manager_cannot_publish_job(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.HIRING_MANAGER)
    job = JobFactory(company=membership.company, status=Job.Status.DRAFT)
    _auth(api_client, membership)

    response = api_client.post(f"/api/v1/companies/acme/jobs/{job.id}/publish/")
    assert response.status_code == 403


@pytest.mark.django_db
def test_hiring_manager_cannot_patch_job(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.HIRING_MANAGER)
    job = JobFactory(company=membership.company)
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/jobs/{job.id}/",
        {"title": "Updated"},
        format="json",
    )
    assert response.status_code == 403
