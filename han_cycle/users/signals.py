from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import User


@receiver(post_save, sender=User)
def index_user(sender, instance, **kwargs):
    instance.indexing()
