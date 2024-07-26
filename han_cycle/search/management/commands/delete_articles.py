# 테스트 데이터 지우는것_개발상태에서는 남겨두기

from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch


class Command(BaseCommand):
    help = "Delete all articles from Elasticsearch"

    def handle(self, *args, **kwargs):
        es = Elasticsearch(["http://elasticsearch:9200"])
        es.indices.delete(index="articles", ignore=[400, 404])
        self.stdout.write(self.style.SUCCESS("Successfully deleted articles index"))
