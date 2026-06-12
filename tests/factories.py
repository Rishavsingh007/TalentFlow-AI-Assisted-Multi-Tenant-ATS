import factory
from django.contrib.auth import get_user_model

from apps.companies.models import Company, CompanyMember

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    role = User.Role.RECRUITER
    password = factory.PostGenerationMethodCall("set_password", "test-password-123")


class CompanyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Company

    name = factory.Sequence(lambda n: f"Company {n}")
    slug = factory.Sequence(lambda n: f"company-{n}")
    industry = "Technology"
    owner = factory.SubFactory(UserFactory, role=User.Role.COMPANY_ADMIN)


class CompanyMemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CompanyMember

    user = factory.SubFactory(UserFactory)
    company = factory.SubFactory(CompanyFactory)
    role = CompanyMember.Role.RECRUITER
