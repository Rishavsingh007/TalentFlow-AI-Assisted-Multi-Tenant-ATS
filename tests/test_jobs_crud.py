import pytest

from apps.jobs.models import Job
from tests.factories import CompanyMemberFactory, JobFactory, UserFactory

REGISTER_URL = "/api/v1/auth/register/"


def _auth_client(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
def test_create_job_as_company_member(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    _auth_client(api_client, membership)

    response = api_client.post(
        "/api/v1/companies/acme/jobs/",
        {
            "title": "Backend Engineer",
            "description": "Python and Django",
            "department": "Engineering",
            "location": "Remote",
            "employment_type": "full_time",
        },
        format="json",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Backend Engineer"
    assert data["status"] == "draft"

    job = Job.objects.get(id=data["id"])
    assert job.company == membership.company


@pytest.mark.django_db
def test_list_company_jobs(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    JobFactory(company=membership.company, title="Job A")
    JobFactory(company=membership.company, title="Job B")
    _auth_client(api_client, membership)

    response = api_client.get("/api/v1/companies/acme/jobs/")

    assert response.status_code == 200
    titles = [j["title"] for j in response.json()["results"]]
    assert "Job A" in titles
    assert "Job B" in titles


@pytest.mark.django_db
def test_retrieve_and_update_job(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, title="Original")
    _auth_client(api_client, membership)

    get_response = api_client.get(f"/api/v1/companies/acme/jobs/{job.id}/")
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Original"

    patch_response = api_client.patch(
        f"/api/v1/companies/acme/jobs/{job.id}/",
        {"title": "Updated Title"},
        format="json",
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["title"] == "Updated Title"


@pytest.mark.django_db
def test_company_jobs_returns_404_for_non_member(api_client):
    CompanyMemberFactory(company__slug="acme")
    outsider = UserFactory()
    api_client.force_authenticate(user=outsider)

    response = api_client.get("/api/v1/companies/acme/jobs/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_company_job_detail_returns_404_for_wrong_company(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    other_job = JobFactory(company__slug="globex")
    _auth_client(api_client, membership)

    response = api_client.get(f"/api/v1/companies/acme/jobs/{other_job.id}/")
    assert response.status_code == 404
