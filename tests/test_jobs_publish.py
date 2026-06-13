import pytest

from apps.jobs.models import Job
from tests.factories import CompanyMemberFactory, JobFactory

REGISTER_URL = "/api/v1/auth/register/"


@pytest.mark.django_db
def test_publish_draft_job(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, status=Job.Status.DRAFT)
    api_client.force_authenticate(user=membership.user)

    response = api_client.post(f"/api/v1/companies/acme/jobs/{job.id}/publish/")

    assert response.status_code == 200
    assert response.json()["status"] == "open"
    job.refresh_from_db()
    assert job.status == Job.Status.OPEN


@pytest.mark.django_db
def test_republish_open_job_returns_400(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, status=Job.Status.OPEN)
    api_client.force_authenticate(user=membership.user)

    response = api_client.post(f"/api/v1/companies/acme/jobs/{job.id}/publish/")

    assert response.status_code == 400


@pytest.mark.django_db
def test_public_list_includes_only_open_jobs(api_client):
    company = CompanyMemberFactory(company__slug="acme").company
    open_job = JobFactory(company=company, status=Job.Status.OPEN, title="Open Role")
    JobFactory(company=company, status=Job.Status.DRAFT, title="Draft Role")

    response = api_client.get("/api/v1/jobs/")

    assert response.status_code == 200
    titles = [j["title"] for j in response.json()["results"]]
    assert "Open Role" in titles
    assert "Draft Role" not in titles
    assert open_job.id in [j["id"] for j in response.json()["results"]]
