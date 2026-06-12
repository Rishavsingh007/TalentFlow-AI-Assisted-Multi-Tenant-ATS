import pytest

from tests.factories import CompanyFactory, CompanyMemberFactory, UserFactory

REGISTER_URL = "/api/v1/auth/register/"
LOGIN_URL = "/api/v1/auth/login/"
REFRESH_URL = "/api/v1/auth/refresh/"


@pytest.mark.django_db
def test_login_returns_tokens(api_client):
    api_client.post(
        REGISTER_URL,
        {
            "email": "login@acme.com",
            "password": "secure-pass-123",
            "company_name": "Login Corp",
        },
        format="json",
    )

    response = api_client.post(
        LOGIN_URL,
        {"email": "login@acme.com", "password": "secure-pass-123"},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert "access" in data
    assert "refresh" in data


@pytest.mark.django_db
def test_refresh_returns_new_access_token(api_client):
    register = api_client.post(
        REGISTER_URL,
        {
            "email": "refresh@acme.com",
            "password": "secure-pass-123",
            "company_name": "Refresh Corp",
        },
        format="json",
    )
    refresh_token = register.json()["tokens"]["refresh"]

    response = api_client.post(REFRESH_URL, {"refresh": refresh_token}, format="json")

    assert response.status_code == 200
    assert "access" in response.json()


@pytest.mark.django_db
def test_company_detail_requires_auth(api_client):
    company = CompanyFactory(slug="secret-co")
    url = f"/api/v1/companies/{company.slug}/"

    response = api_client.get(url)
    assert response.status_code == 401


@pytest.mark.django_db
def test_company_detail_returns_404_for_non_member(api_client):
    company = CompanyFactory(slug="acme")
    other_user = UserFactory(email="outsider@example.com")
    api_client.force_authenticate(user=other_user)

    response = api_client.get(f"/api/v1/companies/{company.slug}/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_company_detail_returns_404_for_unknown_slug(api_client):
    user = UserFactory()
    api_client.force_authenticate(user=user)

    response = api_client.get("/api/v1/companies/does-not-exist/")
    assert response.status_code == 404


@pytest.mark.django_db
def test_company_detail_success_for_member(api_client):
    membership = CompanyMemberFactory(company__slug="member-co")
    api_client.force_authenticate(user=membership.user)

    response = api_client.get(f"/api/v1/companies/{membership.company.slug}/")

    assert response.status_code == 200
    assert response.json()["slug"] == "member-co"


@pytest.mark.django_db
def test_company_patch_requires_admin(api_client):
    membership = CompanyMemberFactory(
        company__slug="patch-co",
        role="recruiter",
    )
    api_client.force_authenticate(user=membership.user)

    response = api_client.patch(
        f"/api/v1/companies/{membership.company.slug}/",
        {"industry": "Finance"},
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_company_patch_success_for_admin(api_client):
    membership = CompanyMemberFactory(
        company__slug="admin-co",
        role="admin",
    )
    api_client.force_authenticate(user=membership.user)

    response = api_client.patch(
        f"/api/v1/companies/{membership.company.slug}/",
        {"industry": "Finance"},
        format="json",
    )
    assert response.status_code == 200
    assert response.json()["industry"] == "Finance"
