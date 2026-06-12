from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User

from .models import Company, CompanyMember
from .utils import generate_company_slug

UserModel = get_user_model()


class RegistrationError(ValidationError):
    pass


@transaction.atomic
def register_company(*, email: str, password: str, company_name: str, industry: str = "") -> tuple[User, Company]:
    email = email.lower().strip()

    if UserModel.objects.filter(email=email).exists():
        raise RegistrationError({"email": "A user with this email already exists."})

    slug = generate_company_slug(company_name)

    user = UserModel.objects.create_user(
        email=email,
        password=password,
        role=User.Role.COMPANY_ADMIN,
    )

    company = Company.objects.create(
        name=company_name.strip(),
        slug=slug,
        industry=industry.strip(),
        owner=user,
    )

    CompanyMember.objects.create(
        user=user,
        company=company,
        role=CompanyMember.Role.ADMIN,
    )

    return user, company
