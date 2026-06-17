from unittest.mock import patch

import pytest
from django.core import mail
from django.core.files.base import ContentFile

from apps.applications.models import Application
from apps.audit.models import AuditLog
from apps.companies.models import CompanyMember
from apps.jobs.models import Job
from apps.ai_scoring.tasks import parse_resume, score_application
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory, make_pdf_file

RESUME_TEXT = "Senior Django engineer with PostgreSQL, Celery, and REST API experience."


def _auth(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
@patch("apps.ai_scoring.tasks.extract_text", return_value=RESUME_TEXT)
def test_parse_resume_sets_parsed_text(mock_extract, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    application = ApplicationFactory()
    application.resume_file.save("resume.pdf", make_pdf_file(), save=True)

    parse_resume(application.id)

    application.refresh_from_db()
    assert application.parsed_resume_text == RESUME_TEXT
    mock_extract.assert_called_once()


@pytest.mark.django_db
def test_score_application_sets_ai_fields():
    application = ApplicationFactory(parsed_resume_text=RESUME_TEXT)

    score_application(application.id)

    application.refresh_from_db()
    assert application.ai_score is not None
    assert 40 <= application.ai_score <= 95
    assert application.ai_summary
    assert application.ai_scored_at is not None

    audit = AuditLog.objects.get(object_id=application.id, action="application.scored")
    assert audit.metadata["score"] == application.ai_score


@pytest.mark.django_db(transaction=True)
@patch("apps.ai_scoring.tasks.extract_text", return_value=RESUME_TEXT)
def test_apply_triggers_parse_and_score_eager(mock_extract, api_client, settings, tmp_path, django_capture_on_commit_callbacks):
    settings.MEDIA_ROOT = tmp_path
    job = JobFactory(status=Job.Status.OPEN)

    response = api_client.post(
        f"/api/v1/jobs/{job.id}/apply/",
        {
            "full_name": "Jane Doe",
            "email": "jane.ai@example.com",
            "phone": "555-1234",
            "resume": make_pdf_file(),
        },
        format="multipart",
    )

    assert response.status_code == 201
    application = Application.objects.get(id=response.json()["id"])
    application.refresh_from_db()
    assert application.parsed_resume_text == RESUME_TEXT
    assert application.ai_score is not None
    assert application.ai_scored_at is not None


@pytest.mark.django_db
@patch("apps.ai_scoring.services.get_scoring_provider")
def test_scoring_failure_creates_audit_log(mock_get_provider):
    class FailingProvider:
        def score(self, job_description, resume_text):
            raise RuntimeError("Provider unavailable")

    mock_get_provider.return_value = FailingProvider()
    application = ApplicationFactory(parsed_resume_text=RESUME_TEXT)

    score_application.max_retries = 0
    score_application.apply(args=[application.id])

    application.refresh_from_db()
    assert application.ai_score is None
    assert AuditLog.objects.filter(
        object_id=application.id,
        action="application.scoring_failed",
    ).exists()


@pytest.mark.django_db
def test_get_score_endpoint(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    application = ApplicationFactory(
        company=membership.company,
        ai_score=82.5,
        ai_summary="Strong backend fit.",
    )
    _auth(api_client, membership)

    response = api_client.get(f"/api/v1/companies/acme/applications/{application.id}/score/")

    assert response.status_code == 200
    assert response.json()["ai_score"] == 82.5
    assert response.json()["ai_summary"] == "Strong backend fit."


@pytest.mark.django_db
@patch("apps.ai_scoring.tasks.score_application.delay")
def test_post_rescore_requires_recruiter(mock_delay, api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.RECRUITER)
    application = ApplicationFactory(company=membership.company)
    _auth(api_client, membership)

    response = api_client.post(f"/api/v1/companies/acme/applications/{application.id}/score/")

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert data["application_id"] == application.id
    mock_delay.assert_called_once()


@pytest.mark.django_db
@patch("apps.ai_scoring.tasks.score_application.delay")
def test_post_rescore_denied_for_hiring_manager(mock_delay, api_client):
    membership = CompanyMemberFactory(company__slug="acme", role=CompanyMember.Role.HIRING_MANAGER)
    application = ApplicationFactory(company=membership.company)
    _auth(api_client, membership)

    response = api_client.post(f"/api/v1/companies/acme/applications/{application.id}/score/")

    assert response.status_code == 403
    mock_delay.assert_not_called()


@pytest.mark.django_db
def test_parse_resume_corrupt_pdf_records_scoring_failure(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    application = ApplicationFactory()
    application.resume_file.save(
        "bad.pdf",
        ContentFile(b"%PDF-1.4\n% fake truncated pdf"),
        save=True,
    )

    parse_resume(application.id)

    application.refresh_from_db()
    assert application.parsed_resume_text == ""
    assert AuditLog.objects.filter(
        object_id=application.id,
        action="application.scoring_failed",
    ).exists()


@pytest.mark.django_db
def test_send_application_received_email():
    application = ApplicationFactory()

    from apps.notifications.tasks import send_application_received_email

    send_application_received_email(application.id)

    assert len(mail.outbox) == 1
    assert application.applicant_email in mail.outbox[0].to
    assert application.job.title in mail.outbox[0].subject
