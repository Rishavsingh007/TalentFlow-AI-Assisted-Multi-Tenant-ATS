import pytest

from apps.applications.models import Application
from tests.factories import ApplicationFactory, CompanyMemberFactory, JobFactory, make_pdf_file

from apps.jobs.models import Job


def _auth(api_client, membership):
    api_client.force_authenticate(user=membership.user)
    return api_client


@pytest.mark.django_db
def test_acme_user_gets_404_on_globex_application_detail(api_client):
    acme_member = CompanyMemberFactory(company__slug="acme")
    globex_member = CompanyMemberFactory(company__slug="globex")
    globex_application = ApplicationFactory(company=globex_member.company)
    _auth(api_client, acme_member)

    response = api_client.get(
        f"/api/v1/companies/globex/applications/{globex_application.id}/"
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_acme_user_gets_404_on_globex_application_stage_update(api_client):
    acme_member = CompanyMemberFactory(company__slug="acme", role="recruiter")
    globex_member = CompanyMemberFactory(company__slug="globex")
    globex_application = ApplicationFactory(
        company=globex_member.company,
        current_stage="Applied",
    )
    _auth(api_client, acme_member)

    response = api_client.patch(
        f"/api/v1/companies/globex/applications/{globex_application.id}/stage/",
        {"current_stage": "Screening"},
        format="json",
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_same_email_applications_isolated_per_tenant(api_client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    acme_member = CompanyMemberFactory(company__slug="acme-iso")
    globex_member = CompanyMemberFactory(company__slug="globex-iso")
    acme_job = JobFactory(company=acme_member.company, status=Job.Status.OPEN)
    globex_job = JobFactory(company=globex_member.company, status=Job.Status.OPEN)

    api_client.post(
        f"/api/v1/jobs/{acme_job.id}/apply/",
        {
            "full_name": "Shared Email Acme",
            "email": "shared@example.com",
            "resume": make_pdf_file(),
        },
        format="multipart",
    )
    api_client.post(
        f"/api/v1/jobs/{globex_job.id}/apply/",
        {
            "full_name": "Shared Email Globex",
            "email": "shared@example.com",
            "resume": make_pdf_file(),
        },
        format="multipart",
    )

    acme_app = Application.objects.get(company=acme_member.company, applicant_email="shared@example.com")
    globex_app = Application.objects.get(company=globex_member.company, applicant_email="shared@example.com")

    _auth(api_client, acme_member)
    acme_detail = api_client.get(
        f"/api/v1/companies/acme-iso/applications/{acme_app.id}/"
    )
    assert acme_detail.status_code == 200
    assert acme_detail.json()["candidate"]["full_name"] == "Shared Email Acme"

    globex_detail = api_client.get(
        f"/api/v1/companies/globex-iso/applications/{globex_app.id}/"
    )
    assert globex_detail.status_code == 404
