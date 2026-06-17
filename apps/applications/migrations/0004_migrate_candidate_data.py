from django.db import migrations


def copy_candidate_data_to_applications(apps, schema_editor):
    Application = apps.get_model("applications", "Application")
    Candidate = apps.get_model("candidates", "Candidate")

    for application in Application.objects.select_related("candidate").iterator():
        candidate = application.candidate
        application.applicant_full_name = candidate.full_name
        application.applicant_email = candidate.email
        application.applicant_phone = candidate.phone or ""
        application.parsed_resume_text = candidate.parsed_resume_text or ""
        if candidate.resume_file:
            application.resume_file.name = candidate.resume_file.name
        application.save(
            update_fields=[
                "applicant_full_name",
                "applicant_email",
                "applicant_phone",
                "parsed_resume_text",
                "resume_file",
            ]
        )

    for candidate in Candidate.objects.iterator():
        company_ids = list(
            Application.objects.filter(candidate=candidate)
            .values_list("company_id", flat=True)
            .distinct()
        )
        if not company_ids:
            continue

        if len(company_ids) == 1:
            candidate.company_id = company_ids[0]
            candidate.save(update_fields=["company_id"])
            continue

        primary_company_id = company_ids[0]
        candidate.company_id = primary_company_id
        candidate.save(update_fields=["company_id"])

        for company_id in company_ids[1:]:
            new_candidate = Candidate.objects.create(
                company_id=company_id,
                email=candidate.email,
                full_name=candidate.full_name,
                phone=candidate.phone or "",
            )
            Application.objects.filter(candidate=candidate, company_id=company_id).update(
                candidate=new_candidate
            )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0003_application_snapshot_fields"),
        ("candidates", "0002_candidate_company"),
    ]

    operations = [
        migrations.RunPython(copy_candidate_data_to_applications, noop_reverse),
    ]
