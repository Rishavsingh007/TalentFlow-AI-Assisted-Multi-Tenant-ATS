import pytest

from apps.audit.models import AuditLog
from apps.jobs.models import DEFAULT_PIPELINE_STAGES, Job
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory, make_pdf_file


def _auth(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
def test_move_stage_creates_audit_log(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    application = ApplicationFactory(job=job, company=membership.company, current_stage="Screening")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Interview"},
        format="json",
    )

    assert response.status_code == 200
    log = AuditLog.objects.get(object_id=application.id, action="application.stage_changed")
    assert log.metadata == {"from_stage": "Screening", "to_stage": "Interview"}
    assert log.actor == membership.user
    assert log.company == membership.company


@pytest.mark.django_db
def test_publish_job_creates_audit_log(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, status=Job.Status.DRAFT)
    _auth(api_client, membership)

    response = api_client.post(f"/api/v1/companies/acme/jobs/{job.id}/publish/")

    assert response.status_code == 200
    log = AuditLog.objects.get(object_id=job.id, action="job.published")
    assert log.actor == membership.user
    assert log.metadata["title"] == job.title
    assert log.metadata["status"] == "open"


@pytest.mark.django_db
def test_submit_application_creates_audit_log(api_client):
    job = JobFactory(status=Job.Status.OPEN)

    response = api_client.post(
        f"/api/v1/jobs/{job.id}/apply/",
        {
            "full_name": "Jane Doe",
            "email": "jane.audit@example.com",
            "phone": "555-1234",
            "resume": make_pdf_file(),
        },
        format="multipart",
    )

    assert response.status_code == 201
    application_id = response.json()["id"]
    log = AuditLog.objects.get(object_id=application_id, action="application.submitted")
    assert log.actor is None
    assert log.metadata["job_id"] == job.id
    assert log.metadata["candidate_email"] == "jane.audit@example.com"


@pytest.mark.django_db
def test_audit_log_list_for_member(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, status=Job.Status.DRAFT)
    _auth(api_client, membership)

    api_client.post(f"/api/v1/companies/acme/jobs/{job.id}/publish/")

    response = api_client.get("/api/v1/companies/acme/audit-logs/")

    assert response.status_code == 200
    assert response.json()["count"] >= 1
    assert response.json()["results"][0]["action"] == "job.published"


@pytest.mark.django_db
def test_audit_log_list_404_for_non_member(api_client):
    CompanyMemberFactory(company__slug="acme")
    outsider = CompanyMemberFactory(company__slug="other-co")
    _auth(api_client, outsider)

    response = api_client.get("/api/v1/companies/acme/audit-logs/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_audit_logs_ordered_newest_first(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    application = ApplicationFactory(job=job, company=membership.company, current_stage="Applied")
    _auth(api_client, membership)

    api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Screening"},
        format="json",
    )
    api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Interview"},
        format="json",
    )

    response = api_client.get("/api/v1/companies/acme/audit-logs/?action=application.stage_changed")
    results = response.json()["results"]

    assert results[0]["metadata"]["to_stage"] == "Interview"
    assert results[1]["metadata"]["to_stage"] == "Screening"


@pytest.mark.django_db
def test_audit_log_list_filter_by_object_type(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, status=Job.Status.DRAFT)
    _auth(api_client, membership)

    api_client.post(f"/api/v1/companies/acme/jobs/{job.id}/publish/")

    response = api_client.get("/api/v1/companies/acme/audit-logs/?object_type=Job")

    assert response.status_code == 200
    assert all(r["object_type"] == "Job" for r in response.json()["results"])
