from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from apps.applications.models import Application


def _group_name(company_id: int) -> str:
    return f"company_{company_id}_dashboard"


def _broadcast(company_id: int, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        _group_name(company_id),
        {"type": "dashboard.event", "payload": payload},
    )


def broadcast_application_received(application_id: int) -> None:
    application = Application.objects.select_related("candidate", "job", "company").get(
        id=application_id
    )
    _broadcast(
        application.company_id,
        {
            "event": "application.received",
            "application_id": application.id,
            "job_id": application.job_id,
            "job_title": application.job.title,
            "candidate_name": application.applicant_full_name,
            "candidate_email": application.applicant_email,
            "current_stage": application.current_stage,
            "timestamp": timezone.now().isoformat(),
        },
    )


def broadcast_application_scored(application: Application) -> None:
    _broadcast(
        application.company_id,
        {
            "event": "application.scored",
            "application_id": application.id,
            "ai_score": application.ai_score,
            "ai_summary": application.ai_summary,
            "timestamp": timezone.now().isoformat(),
        },
    )


def broadcast_stage_changed(application: Application, *, actor, from_stage: str) -> None:
    _broadcast(
        application.company_id,
        {
            "event": "application.stage_changed",
            "application_id": application.id,
            "from_stage": from_stage,
            "to_stage": application.current_stage,
            "actor": actor.email if actor else None,
            "timestamp": timezone.now().isoformat(),
        },
    )
