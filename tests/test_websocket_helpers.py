import pytest
from rest_framework_simplejwt.tokens import AccessToken

from apps.companies.access import get_company_membership
from tests.factories import CompanyMemberFactory


@pytest.mark.django_db
def test_get_company_membership_for_ws_slug():
    membership = CompanyMemberFactory(company__slug="acme-corp")
    result = get_company_membership(slug="acme-corp", user=membership.user)
    assert result.company.slug == "acme-corp"


@pytest.mark.django_db
def test_access_token_authenticates_user():
    membership = CompanyMemberFactory(company__slug="acme-corp")
    token = AccessToken.for_user(membership.user)
    assert int(token["user_id"]) == membership.user.id
