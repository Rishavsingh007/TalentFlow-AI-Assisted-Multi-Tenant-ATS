import pytest
from django.contrib.auth import get_user_model

from apps.companies.models import Company, CompanyMember

User = get_user_model()

REGISTER_URL = "/api/v1/auth/register/"


@pytest.mark.django_db
def test_register_creates_company_user_and_membership(api_client):
    payload = {
        "email": "admin@acme.com",
        "password": "secure-pass-123",
        "company_name": "Acme Corp",
        "industry": "Technology",
    }
    response = api_client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "admin@acme.com"
    assert data["user"]["role"] == "company_admin"
    assert data["company"]["name"] == "Acme Corp"
    assert data["company"]["slug"] == "acme-corp"
    assert "access" in data["tokens"]
    assert "refresh" in data["tokens"]

    user = User.objects.get(email="admin@acme.com")
    company = Company.objects.get(slug="acme-corp")
    assert company.owner == user
    assert CompanyMember.objects.filter(
        user=user, company=company, role=CompanyMember.Role.ADMIN
    ).exists()


@pytest.mark.django_db
def test_register_duplicate_email_returns_400(api_client):
    payload = {
        "email": "dup@acme.com",
        "password": "secure-pass-123",
        "company_name": "Acme Corp",
    }
    api_client.post(REGISTER_URL, payload, format="json")
    response = api_client.post(REGISTER_URL, payload, format="json")

    assert response.status_code == 400
    assert "email" in response.json()


@pytest.mark.django_db
def test_register_duplicate_company_name_gets_unique_slug(api_client):
    payload1 = {
        "email": "admin1@acme.com",
        "password": "secure-pass-123",
        "company_name": "Acme Corp",
    }
    payload2 = {
        "email": "admin2@acme.com",
        "password": "secure-pass-123",
        "company_name": "Acme Corp",
    }
    r1 = api_client.post(REGISTER_URL, payload1, format="json")
    r2 = api_client.post(REGISTER_URL, payload2, format="json")

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["company"]["slug"] == "acme-corp"
    assert r2.json()["company"]["slug"] == "acme-corp-2"
