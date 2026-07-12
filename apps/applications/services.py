from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from apps.applications.models import Application
from apps.applications.transitions import status_for_stage, validate_stage_transition
from apps.audit.services import log_action
from apps.candidates.models import Candidate
from apps.core.uploads import validate_resume_upload
from apps.jobs.models import Job


class DuplicateApplicationError(ValidationError):
    pass


@transaction.atomic
def submit_application(
    job: Job, *, full_name: str, email: str, phone: str, resume_file
) -> Application:
    if job.status != Job.Status.OPEN or not job.company.is_active:
        raise ValidationError({"job": "This job is not accepting applications."})

    validate_resume_upload(resume_file)

    email = email.lower().strip()
    full_name = full_name.strip()
    phone = phone.strip()
    company = job.company

    candidate, created = Candidate.objects.select_for_update().get_or_create(
        company=company,
        email=email,
        defaults={"full_name": full_name, "phone": phone},
    )
    if not created:
        candidate.full_name = full_name
        candidate.phone = phone
        candidate.save(update_fields=["full_name", "phone"])

    if Application.objects.filter(job=job, candidate=candidate).exists():
        raise DuplicateApplicationError({"detail": "You have already applied to this job."})

    try:
        application = Application.objects.create(
            job=job,
            candidate=candidate,
            company=company,
            applicant_full_name=full_name,
            applicant_email=email,
            applicant_phone=phone,
            resume_file=resume_file,
            current_stage="Applied",
        )
    except IntegrityError:
        raise DuplicateApplicationError(
            {"detail": "You have already applied to this job."}
        ) from None

    log_action(
        actor=None,
        action="application.submitted",
        instance=application,
        metadata={
            "job_id": job.id,
            "job_title": job.title,
            "candidate_email": email,
        },
    )

    from apps.ai_scoring.tasks import parse_resume
    from apps.notifications.broadcast import broadcast_application_received
    from apps.notifications.tasks import send_application_received_email

    application_id = application.id
    transaction.on_commit(lambda: parse_resume.delay(application_id))
    transaction.on_commit(lambda: send_application_received_email.delay(application_id))
    transaction.on_commit(lambda: broadcast_application_received(application_id))

    return application


@transaction.atomic
def move_stage(application: Application, *, new_stage: str, actor) -> Application:
    validate_stage_transition(application, new_stage)
    old_stage = application.current_stage
    application.current_stage = new_stage
    application.status = status_for_stage(new_stage)
    application.save(update_fields=["current_stage", "status"])
    log_action(
        actor=actor,
        action="application.stage_changed",
        instance=application,
        metadata={"from_stage": old_stage, "to_stage": new_stage},
    )
    from apps.notifications.broadcast import broadcast_stage_changed

    broadcast_stage_changed(application, actor=actor, from_stage=old_stage)
    return application
