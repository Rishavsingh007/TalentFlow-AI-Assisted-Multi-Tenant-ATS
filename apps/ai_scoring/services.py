from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.applications.models import Application
from apps.audit.services import log_action

from .providers.factory import get_scoring_provider

User = get_user_model()


def run_scoring(application: Application, *, actor=None) -> Application:
    if not application.candidate.parsed_resume_text.strip():
        raise ValueError("Resume has not been parsed yet")

    provider = get_scoring_provider()
    result = provider.score(application.job.description, application.candidate.parsed_resume_text)

    application.ai_score = result.score
    application.ai_summary = result.summary
    application.ai_scored_at = timezone.now()
    application.save(update_fields=["ai_score", "ai_summary", "ai_scored_at"])

    log_action(
        actor=actor,
        action="application.scored",
        instance=application,
        metadata={"score": result.score, "summary": result.summary},
    )
    # TODO Phase 6: broadcast application.scored

    return application


def record_scoring_failure(application: Application, *, error: str, actor=None) -> None:
    log_action(
        actor=actor,
        action="application.scoring_failed",
        instance=application,
        metadata={"error": error},
    )


def rescore_application(application: Application, *, actor) -> Application:
    from .tasks import score_application

    score_application.delay(application.id, actor_id=actor.id)
    return application
