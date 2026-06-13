import pytest

from apps.applications.models import Application
from apps.jobs.models import DEFAULT_PIPELINE_STAGES, Job
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory


def _auth(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
def test_move_stage_screening_to_interview(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role="recruiter")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    application = ApplicationFactory(job=job, company=membership.company, current_stage="Screening")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Interview"},
        format="json",
    )

    assert response.status_code == 200
    assert response.json()["current_stage"] == "Interview"
    application.refresh_from_db()
    assert application.status == Application.Status.ACTIVE


@pytest.mark.django_db
def test_move_stage_to_hired_sets_status(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role="admin")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    application = ApplicationFactory(job=job, company=membership.company, current_stage="Offer")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Hired"},
        format="json",
    )

    assert response.status_code == 200
    application.refresh_from_db()
    assert application.current_stage == "Hired"
    assert application.status == Application.Status.HIRED


@pytest.mark.django_db
def test_move_stage_to_rejected_sets_status(api_client):
    membership = CompanyMemberFactory(company__slug="acme", role="recruiter")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    application = ApplicationFactory(job=job, company=membership.company, current_stage="Screening")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Rejected"},
        format="json",
    )

    assert response.status_code == 200
    application.refresh_from_db()
    assert application.status == Application.Status.REJECTED


@pytest.mark.django_db
def test_move_stage_invalid_stage_returns_400(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    application = ApplicationFactory(company=membership.company, current_stage="Applied")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "NotARealStage"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_move_stage_same_stage_returns_400(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    application = ApplicationFactory(company=membership.company, current_stage="Applied")
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Applied"},
        format="json",
    )

    assert response.status_code == 400


@pytest.mark.django_db
def test_move_stage_from_terminal_stage_returns_400(api_client):
    membership = CompanyMemberFactory(company__slug="acme")
    job = JobFactory(company=membership.company, pipeline_stages=list(DEFAULT_PIPELINE_STAGES))
    application = ApplicationFactory(
        job=job,
        company=membership.company,
        current_stage="Hired",
        status=Application.Status.HIRED,
    )
    _auth(api_client, membership)

    response = api_client.patch(
        f"/api/v1/companies/acme/applications/{application.id}/stage/",
        {"current_stage": "Interview"},
        format="json",
    )

    assert response.status_code == 400
