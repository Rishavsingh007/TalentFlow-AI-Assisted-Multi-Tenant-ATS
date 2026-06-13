import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.applications.models import Application
from apps.candidates.models import Candidate
from tests.factories import CompanyMemberFactory, JobFactory, make_pdf_file

from apps.jobs.models import Job


@pytest.mark.django_db
def test_apply_creates_candidate_and_application(api_client):
    company = CompanyMemberFactory().company
    job = JobFactory(company=company, status=Job.Status.OPEN)

    response = api_client.post(
        f"/api/v1/jobs/{job.id}/apply/",
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "555-1234",
            "resume": make_pdf_file(),
        },
        format="multipart",
    )

    assert response.status_code == 201
    data = response.json()
    assert data["current_stage"] == "Applied"
    assert data["job_id"] == job.id

    candidate = Candidate.objects.get(email="jane@example.com")
    assert candidate.full_name == "Jane Doe"
    assert Application.objects.filter(job=job, candidate=candidate).exists()


@pytest.mark.django_db
def test_duplicate_apply_returns_400(api_client):
    company = CompanyMemberFactory().company
    job = JobFactory(company=company, status=Job.Status.OPEN)
    payload = {
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "555-1234",
        "resume": make_pdf_file(),
    }

    first = api_client.post(f"/api/v1/jobs/{job.id}/apply/", payload, format="multipart")
    assert first.status_code == 201

    payload["resume"] = make_pdf_file()
    second = api_client.post(f"/api/v1/jobs/{job.id}/apply/", payload, format="multipart")
    assert second.status_code == 400


@pytest.mark.django_db
def test_apply_to_closed_job_returns_404(api_client):
    job = JobFactory(status=Job.Status.DRAFT)

    response = api_client.post(
        f"/api/v1/jobs/{job.id}/apply/",
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "resume": make_pdf_file(),
        },
        format="multipart",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_apply_rejects_invalid_file_type(api_client):
    job = JobFactory(status=Job.Status.OPEN)
    bad_file = SimpleUploadedFile("resume.txt", b"not a resume", content_type="text/plain")

    response = api_client.post(
        f"/api/v1/jobs/{job.id}/apply/",
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "resume": bad_file,
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "resume" in response.json()


@pytest.mark.django_db
def test_apply_rejects_oversized_file(api_client):
    job = JobFactory(status=Job.Status.OPEN)
    big_file = SimpleUploadedFile(
        "resume.pdf",
        b"%PDF-1.4" + (b"x" * (5 * 1024 * 1024)),
        content_type="application/pdf",
    )

    response = api_client.post(
        f"/api/v1/jobs/{job.id}/apply/",
        {
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "resume": big_file,
        },
        format="multipart",
    )

    assert response.status_code == 400
    assert "resume" in response.json()
