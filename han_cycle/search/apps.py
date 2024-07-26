from django.apps import AppConfig
from elasticsearch_dsl.connections import connections

from .search_indexes import ArticleIndex


class SearchConfig(AppConfig):
    name = "search"

    def ready(self):
        import search.signals

        connections.create_connection(hosts=["http://elasticsearch:9200"])
        ArticleIndex.init()  # 인덱스 초기화
