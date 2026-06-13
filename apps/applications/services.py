from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.applications.models import Application
from apps.candidates.models import Candidate
from apps.core.uploads import validate_resume_upload
from apps.jobs.models import Job


class DuplicateApplicationError(ValidationError):
    pass


@transaction.atomic
def submit_application(job: Job, *, full_name: str, email: str, phone: str, resume_file) -> Application:
    if job.status != Job.Status.OPEN or not job.company.is_active:
        raise ValidationError({"job": "This job is not accepting applications."})

    validate_resume_upload(resume_file)

    email = email.lower().strip()
    candidate = Candidate.objects.filter(email=email).first()

    if candidate:
        if Application.objects.filter(job=job, candidate=candidate).exists():
            raise DuplicateApplicationError(
                {"detail": "You have already applied to this job."}
            )
        candidate.full_name = full_name.strip()
        candidate.phone = phone.strip()
        candidate.resume_file = resume_file
        candidate.save(update_fields=["full_name", "phone", "resume_file"])
    else:
        candidate = Candidate.objects.create(
            email=email,
            full_name=full_name.strip(),
            phone=phone.strip(),
            resume_file=resume_file,
        )

    application = Application.objects.create(
        job=job,
        candidate=candidate,
        company=job.company,
        current_stage="Applied",
    )

    # TODO Phase 5: parse_resume.delay(application.id)

    return application


@transaction.atomic
def move_stage(application: Application, *, new_stage: str, actor) -> Application:
    from apps.applications.transitions import status_for_stage, validate_stage_transition

    validate_stage_transition(application, new_stage)
    application.current_stage = new_stage
    application.status = status_for_stage(new_stage)
    application.save(update_fields=["current_stage", "status"])
    # TODO Phase 4: audit.log_action(actor, "application.stage_changed", application, metadata={...})
    # TODO Phase 6: notifications.broadcast_stage_changed(application.company_id, ...)
    return application
