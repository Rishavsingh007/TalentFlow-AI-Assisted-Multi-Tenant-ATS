import logging

from celery import shared_task
from django.contrib.auth import get_user_model

from apps.applications.models import Application
from apps.core.scan import NoOpScanProvider

from .parsing import ResumeParseError, extract_text
from .services import record_scoring_failure, run_scoring

logger = logging.getLogger(__name__)

User = get_user_model()


@shared_task(
    bind=True,
    autoretry_for=(OSError,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def parse_resume(self, application_id: int) -> None:
    application = Application.objects.select_related("candidate", "job").get(id=application_id)
    candidate = application.candidate
    resume_path = candidate.resume_file.path

    NoOpScanProvider().scan(resume_path)

    try:
        parsed_text = extract_text(resume_path)
    except ResumeParseError as exc:
        logger.warning("Resume parse failed for application %s: %s", application_id, exc)
        record_scoring_failure(application, error=str(exc))
        return

    candidate.parsed_resume_text = parsed_text
    candidate.save(update_fields=["parsed_resume_text"])

    score_application.delay(application_id)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def score_application(self, application_id: int, *, actor_id: int | None = None) -> None:
    application = Application.objects.select_related("candidate", "job").get(id=application_id)
    actor = User.objects.filter(id=actor_id).first() if actor_id else None

    try:
        if not application.candidate.parsed_resume_text.strip():
            raise ValueError("Resume text is empty")

        run_scoring(application, actor=actor)
    except Exception as exc:
        logger.exception("Scoring failed for application %s", application_id)
        if self.request.retries >= self.max_retries:
            record_scoring_failure(application, error=str(exc), actor=actor)
            return
        raise self.retry(exc=exc)
