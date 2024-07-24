from django.db import models
from elasticsearch_dsl import Date, Document, Text, connections

# Elasticsearch 연결 설정 (URL에 'http://' 포함)
connections.create_connection(hosts=["http://elasticsearch:9200"])


class ArticleIndex(Document):
    title = Text()
    content = Text()
    published_date = Date()

    class Index:
        name = "articles"

    def save(self, **kwargs):
        return super().save(**kwargs)


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    published_date = models.DateField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        article_index = ArticleIndex(
            meta={"id": self.id},
            title=self.title,
            content=self.content,
            published_date=self.published_date,
        )
        article_index.save()

    def delete(self, *args, **kwargs):
        article_index = ArticleIndex.get(id=self.id)
        article_index.delete()
        super().delete(*args, **kwargs)
