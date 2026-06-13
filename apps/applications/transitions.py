from rest_framework.exceptions import ValidationError

from apps.applications.models import Application

TERMINAL_STAGES = {"Rejected", "Hired"}


def status_for_stage(stage: str) -> str:
    if stage == "Rejected":
        return Application.Status.REJECTED
    if stage == "Hired":
        return Application.Status.HIRED
    return Application.Status.ACTIVE


def validate_stage_transition(application: Application, new_stage: str) -> None:
    if application.status != Application.Status.ACTIVE:
        raise ValidationError({"current_stage": "Cannot move an inactive application."})

    if application.current_stage in TERMINAL_STAGES:
        raise ValidationError({"current_stage": "Cannot move an application from a terminal stage."})

    if new_stage not in application.job.pipeline_stages:
        raise ValidationError({"current_stage": "Stage is not valid for this job's pipeline."})

    if new_stage == application.current_stage:
        raise ValidationError({"current_stage": "Application is already in this stage."})
