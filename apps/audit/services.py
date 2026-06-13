from apps.applications.models import Application
from apps.companies.models import Company
from apps.jobs.models import Job

from .models import AuditLog


def _resolve_company(instance) -> Company:
    if isinstance(instance, Application):
        return instance.company
    if isinstance(instance, Job):
        return instance.company
    company = getattr(instance, "company", None)
    if company is not None:
        return company
    raise ValueError(f"Cannot resolve company for audit log instance: {type(instance).__name__}")


def _resolve_actor(actor):
    if actor is None:
        return None
    if getattr(actor, "is_authenticated", False):
        return actor
    return None


def log_action(*, actor, action: str, instance, metadata: dict | None = None) -> AuditLog:
    return AuditLog.objects.create(
        company=_resolve_company(instance),
        actor=_resolve_actor(actor),
        action=action,
        object_type=instance.__class__.__name__,
        object_id=instance.pk,
        metadata=metadata or {},
    )
