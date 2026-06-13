import pytest

from tests.factories import ApplicationFactory, CompanyMemberFactory


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
