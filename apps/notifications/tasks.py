from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string

from apps.applications.models import Application


@shared_task
def send_application_received_email(application_id: int) -> None:
    application = Application.objects.select_related("candidate", "job", "company").get(
        id=application_id
    )
    candidate = application.candidate
    job = application.job

    message = render_to_string(
        "notifications/application_received.txt",
        {
            "candidate_name": application.applicant_full_name,
            "job_title": job.title,
            "company_name": application.company.name,
        },
    )

    send_mail(
        subject=f"Application received — {job.title}",
        message=message,
        from_email=None,
        recipient_list=[candidate.email],
    )
