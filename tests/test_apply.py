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

    candidate = Candidate.objects.get(company=company, email="jane@example.com")
    assert candidate.full_name == "Jane Doe"
    application = Application.objects.get(job=job, candidate=candidate)
    assert application.applicant_full_name == "Jane Doe"
    assert application.applicant_email == "jane@example.com"


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


@pytest.mark.django_db
def test_same_email_across_tenants_does_not_overwrite(api_client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    acme = CompanyMemberFactory(company__slug="acme-apply").company
    globex = CompanyMemberFactory(company__slug="globex-apply").company
    acme_job = JobFactory(company=acme, status=Job.Status.OPEN)
    globex_job = JobFactory(company=globex, status=Job.Status.OPEN)

    acme_response = api_client.post(
        f"/api/v1/jobs/{acme_job.id}/apply/",
        {
            "full_name": "Alice Acme",
            "email": "alice@example.com",
            "phone": "111",
            "resume": make_pdf_file("alice-acme.pdf"),
        },
        format="multipart",
    )
    assert acme_response.status_code == 201
    acme_app_id = acme_response.json()["id"]

    globex_response = api_client.post(
        f"/api/v1/jobs/{globex_job.id}/apply/",
        {
            "full_name": "Alice Globex",
            "email": "alice@example.com",
            "phone": "222",
            "resume": make_pdf_file("alice-globex.pdf"),
        },
        format="multipart",
    )
    assert globex_response.status_code == 201

    acme_app = Application.objects.get(id=acme_app_id)
    assert acme_app.applicant_full_name == "Alice Acme"
    assert acme_app.applicant_phone == "111"

    assert Candidate.objects.filter(company=acme, email="alice@example.com").exists()
    assert Candidate.objects.filter(company=globex, email="alice@example.com").exists()
    assert Candidate.objects.filter(email="alice@example.com").count() == 2
