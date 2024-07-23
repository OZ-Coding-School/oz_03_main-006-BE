from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Article
from .search_indexes import ArticleIndex


@receiver(post_save, sender=Article)
def index_article(sender, instance, **kwargs):
    article = ArticleIndex(
        meta={"id": instance.id},
        title=instance.title,
        content=instance.content,
        published_date=instance.published_date,
    )
    article.save()


@receiver(post_delete, sender=Article)
def delete_article(sender, instance, **kwargs):
    article = ArticleIndex(meta={"id": instance.id})
    article.delete()
