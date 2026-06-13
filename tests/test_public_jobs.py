import pytest

from tests.factories import CompanyMemberFactory, JobFactory

from apps.jobs.models import Job


@pytest.mark.django_db
def test_public_job_list_paginated(api_client):
    company = CompanyMemberFactory().company
    JobFactory.create_batch(3, company=company, status=Job.Status.OPEN)

    response = api_client.get("/api/v1/jobs/")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3


@pytest.mark.django_db
def test_public_job_detail_for_open_job(api_client):
    company = CompanyMemberFactory(company__slug="acme").company
    job = JobFactory(company=company, status=Job.Status.OPEN, title="Public Role")

    response = api_client.get(f"/api/v1/jobs/{job.id}/")

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Public Role"
    assert data["company_slug"] == "acme"


@pytest.mark.django_db
def test_public_job_detail_returns_404_for_draft(api_client):
    job = JobFactory(status=Job.Status.DRAFT)

    response = api_client.get(f"/api/v1/jobs/{job.id}/")

    assert response.status_code == 404
