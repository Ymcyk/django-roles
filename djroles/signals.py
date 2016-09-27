from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Role

@receiver(post_delete, sender=Role)
def auto_delete_group_with_role(sender, instance, **kwargs):
    instance.group.delete()

