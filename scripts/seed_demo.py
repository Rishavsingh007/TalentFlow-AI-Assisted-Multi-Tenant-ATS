#!/usr/bin/env python
"""Seed Acme and Globex demo tenants with jobs and pipeline applications."""

import os
import sys
from pathlib import Path

import django
from django.core.files.base import ContentFile
from django.db import transaction

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from apps.accounts.models import User  # noqa: E402
from apps.applications.models import Application  # noqa: E402
from apps.applications.transitions import status_for_stage  # noqa: E402
from apps.candidates.models import Candidate  # noqa: E402
from apps.companies.models import Company, CompanyMember  # noqa: E402
from apps.jobs.models import DEFAULT_PIPELINE_STAGES, Job  # noqa: E402

DEMO_PASSWORD = "demo-password-123"
DEMO_PDF = b"%PDF-1.4 demo resume for TalentFlow seed"


def _ensure_user(*, email: str, role: str) -> User:
    user, created = User.objects.get_or_create(
        email=email,
        defaults={"role": role},
    )
    if created or not user.has_usable_password():
        user.set_password(DEMO_PASSWORD)
        user.role = role
        user.save(update_fields=["password", "role"])
    return user


def _ensure_company(*, name: str, slug: str, owner: User, industry: str = "Technology") -> Company:
    company, _ = Company.objects.update_or_create(
        slug=slug,
        defaults={"name": name, "owner": owner, "industry": industry, "is_active": True},
    )
    return company


def _ensure_membership(*, user: User, company: Company, role: str) -> None:
    CompanyMember.objects.update_or_create(
        user=user,
        company=company,
        defaults={"role": role},
    )


def _ensure_open_job(*, company: Company, title: str, description: str) -> Job:
    job, created = Job.objects.get_or_create(
        company=company,
        title=title,
        defaults={
            "description": description,
            "department": "Engineering",
            "location": "Remote",
            "employment_type": Job.EmploymentType.FULL_TIME,
            "status": Job.Status.OPEN,
            "pipeline_stages": list(DEFAULT_PIPELINE_STAGES),
        },
    )
    if not created and job.status != Job.Status.OPEN:
        job.status = Job.Status.OPEN
        job.save(update_fields=["status"])
    return job


def _ensure_application(*, job: Job, email: str, full_name: str, stage: str) -> Application:
    candidate, _ = Candidate.objects.get_or_create(
        company=job.company,
        email=email,
        defaults={"full_name": full_name, "phone": "555-0100"},
    )

    resume_name = f"{email.split('@')[0]}.pdf"
    application, created = Application.objects.get_or_create(
        job=job,
        candidate=candidate,
        defaults={
            "company": job.company,
            "applicant_full_name": full_name,
            "applicant_email": email,
            "applicant_phone": "555-0100",
            "resume_file": ContentFile(DEMO_PDF, name=resume_name),
            "current_stage": stage,
            "status": status_for_stage(stage),
        },
    )
    if not created and (application.current_stage != stage or application.status != status_for_stage(stage)):
        application.current_stage = stage
        application.status = status_for_stage(stage)
        application.save(update_fields=["current_stage", "status"])
    elif created is False and not application.resume_file:
        application.resume_file.save(resume_name, ContentFile(DEMO_PDF), save=True)
    return application


@transaction.atomic
def seed_acme() -> tuple[Company, int, int]:
    admin = _ensure_user(email="admin@acme.com", role=User.Role.COMPANY_ADMIN)
    recruiter = _ensure_user(email="recruiter@acme.com", role=User.Role.RECRUITER)
    company = _ensure_company(name="Acme Corp", slug="acme-corp", owner=admin)
    _ensure_membership(user=admin, company=company, role=CompanyMember.Role.ADMIN)
    _ensure_membership(user=recruiter, company=company, role=CompanyMember.Role.RECRUITER)

    jobs = [
        _ensure_open_job(
            company=company,
            title="Backend Engineer",
            description="Build multi-tenant APIs with Django and PostgreSQL.",
        ),
        _ensure_open_job(
            company=company,
            title="Frontend Engineer",
            description="Ship the React demo UI for recruiter pipeline workflows.",
        ),
    ]

    applications_spec = [
        (jobs[0], "alice@example.com", "Alice Smith", "Applied"),
        (jobs[0], "bob@example.com", "Bob Jones", "Screening"),
        (jobs[0], "carol@example.com", "Carol Lee", "Interview"),
        (jobs[0], "dan@example.com", "Dan Kim", "Rejected"),
        (jobs[0], "eve@example.com", "Eve Patel", "Hired"),
        (jobs[1], "frank@example.com", "Frank Wu", "Applied"),
        (jobs[1], "grace@example.com", "Grace Hall", "Screening"),
    ]

    for job, email, name, stage in applications_spec:
        _ensure_application(job=job, email=email, full_name=name, stage=stage)

    return company, len(jobs), len(applications_spec)


@transaction.atomic
def seed_globex() -> tuple[Company, int, int]:
    recruiter = _ensure_user(email="recruiter@globex.com", role=User.Role.RECRUITER)
    company = _ensure_company(name="Globex Inc", slug="globex-inc", owner=recruiter, industry="Manufacturing")
    _ensure_membership(user=recruiter, company=company, role=CompanyMember.Role.RECRUITER)

    job = _ensure_open_job(
        company=company,
        title="Operations Analyst",
        description="Cross-tenant isolation demo tenant — not for Acme users.",
    )

    applications_spec = [
        (job, "henry@example.com", "Henry Ford", "Applied"),
        (job, "iris@example.com", "Iris Chen", "Screening"),
    ]

    for job_item, email, name, stage in applications_spec:
        _ensure_application(job=job_item, email=email, full_name=name, stage=stage)

    return company, 1, len(applications_spec)


def main() -> None:
    acme, acme_jobs, acme_apps = seed_acme()
    globex, globex_jobs, globex_apps = seed_globex()

    print("TalentFlow demo seed complete\n")
    print(f"{'Tenant':<12} {'Slug':<14} {'Jobs':<6} {'Applications'}")
    print(f"{'Acme Corp':<12} {acme.slug:<14} {acme_jobs:<6} {acme_apps}")
    print(f"{'Globex Inc':<12} {globex.slug:<14} {globex_jobs:<6} {globex_apps}")
    print()
    print("Credentials (password for all): demo-password-123")
    print("  admin@acme.com       — Acme admin")
    print("  recruiter@acme.com   — Acme recruiter")
    print("  recruiter@globex.com — Globex recruiter")


if __name__ == "__main__":
    main()
