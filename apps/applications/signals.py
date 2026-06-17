from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Application


@receiver(pre_delete, sender=Application)
def delete_application_resume_file(sender, instance, **kwargs):
    if instance.resume_file:
        instance.resume_file.delete(save=False)
