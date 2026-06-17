import factory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.applications.models import Application
from apps.audit.models import AuditLog
from apps.candidates.models import Candidate
from apps.companies.models import Company, CompanyMember
from apps.jobs.models import Job

User = get_user_model()


def make_pdf_file(name="resume.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 test resume content", content_type="application/pdf")


def make_docx_file(name="resume.docx"):
    return SimpleUploadedFile(
        name,
        b"PK\x03\x04 fake docx content",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


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


class JobFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Job

    company = factory.SubFactory(CompanyFactory)
    title = factory.Sequence(lambda n: f"Software Engineer {n}")
    description = "Build great software."
    department = "Engineering"
    location = "Remote"
    employment_type = Job.EmploymentType.FULL_TIME
    status = Job.Status.DRAFT


class CandidateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Candidate

    company = factory.SubFactory(CompanyFactory)
    email = factory.Sequence(lambda n: f"candidate{n}@example.com")
    full_name = factory.Sequence(lambda n: f"Candidate {n}")
    phone = "555-0100"


class ApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Application

    job = factory.SubFactory(JobFactory, status=Job.Status.OPEN)
    company = factory.LazyAttribute(lambda obj: obj.job.company)
    candidate = factory.SubFactory(
        CandidateFactory,
        company=factory.SelfAttribute("..company"),
        email=factory.Sequence(lambda n: f"app-candidate{n}@example.com"),
        full_name=factory.Sequence(lambda n: f"Applicant {n}"),
    )
    applicant_full_name = factory.LazyAttribute(lambda obj: obj.candidate.full_name)
    applicant_email = factory.LazyAttribute(lambda obj: obj.candidate.email)
    applicant_phone = factory.LazyAttribute(lambda obj: obj.candidate.phone)
    resume_file = factory.LazyFunction(lambda: make_pdf_file())
    current_stage = "Applied"


class AuditLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = AuditLog

    company = factory.SubFactory(CompanyFactory)
    actor = factory.SubFactory(UserFactory)
    action = "application.stage_changed"
    object_type = "Application"
    object_id = factory.Sequence(lambda n: n + 1)
    metadata = factory.LazyFunction(dict)
