import pytest

from apps.jobs.models import Job
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory


def _auth(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
def test_list_applications_for_company_member(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, status=Job.Status.OPEN)
    ApplicationFactory(job=job, company=membership.company, current_stage="Screening")
    _auth(api_client, membership)

    response = api_client.get("/api/v1/companies/acme/applications/")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["current_stage"] == "Screening"


@pytest.mark.django_db
def test_list_applications_filter_by_job(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job_a = JobFactory(company=membership.company, title="Job A")
    job_b = JobFactory(company=membership.company, title="Job B")
    ApplicationFactory(job=job_a, company=membership.company)
    ApplicationFactory(job=job_b, company=membership.company)
    _auth(api_client, membership)

    response = api_client.get(f"/api/v1/companies/acme/applications/?job={job_a.id}")

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["results"][0]["job"]["id"] == job_a.id


@pytest.mark.django_db
def test_list_applications_filter_by_stage_and_status(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company)
    ApplicationFactory(
        job=job, company=membership.company, current_stage="Interview", status="active"
    )
    ApplicationFactory(
        job=job,
        company=membership.company,
        current_stage="Rejected",
        status="rejected",
    )
    _auth(api_client, membership)

    stage_response = api_client.get("/api/v1/companies/acme/applications/?current_stage=Interview")
    assert stage_response.status_code == 200
    assert stage_response.json()["count"] == 1

    status_response = api_client.get("/api/v1/companies/acme/applications/?status=rejected")
    assert status_response.status_code == 200
    assert status_response.json()["count"] == 1


@pytest.mark.django_db
def test_application_detail_for_member(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    application = ApplicationFactory(company=membership.company, current_stage="Applied")
    _auth(api_client, membership)

    response = api_client.get(f"/api/v1/companies/acme/applications/{application.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == application.id
    assert "pipeline_stages" in data
    assert data["candidate"]["email"] == application.candidate.email


@pytest.mark.django_db
def test_application_list_returns_404_for_non_member(api_client):
    CompanyMemberFactory(company__slug="acme")
    outsider_membership = CompanyMemberFactory(company__slug="other-co")
    _auth(api_client, outsider_membership)

    response = api_client.get("/api/v1/companies/acme/applications/")
    assert response.status_code == 404
