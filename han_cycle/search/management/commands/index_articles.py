from django.core.management.base import BaseCommand
from search.models import Article
from search.search_indexes import ArticleIndex


class Command(BaseCommand):
    help = "Index all articles to Elasticsearch"

    def handle(self, *args, **kwargs):
        articles = Article.objects.all()
        for article in articles:
            article_index = ArticleIndex(
                meta={"id": article.id},
                title=article.title,
                content=article.content,
                published_date=article.published_date,
            )
            article_index.save()
        self.stdout.write(self.style.SUCCESS("Successfully indexed articles"))
