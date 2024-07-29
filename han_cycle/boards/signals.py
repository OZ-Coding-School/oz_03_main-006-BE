from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Post


@receiver(post_save, sender=Post)
def index_post(sender, instance, **kwargs):
    instance.indexing()
