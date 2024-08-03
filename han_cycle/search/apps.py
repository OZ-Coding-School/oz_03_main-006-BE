# from django.apps import AppConfig
# from django.conf import settings
# from elasticsearch_dsl.connections import connections

# from .search_index import LocationIndex, PostIndex, UserIndex


# class SearchConfig(AppConfig):
#     default_auto_field = "django.db.models.BigAutoField"
#     name = "search"

#     def ready(self):
#         # Elasticsearch 연결을 설정합니다.
#         connections.create_connection(**settings.ELASTICSEARCH_DSL["default"])

#         # 인덱스를 초기화합니다.
#         PostIndex.init()
#         UserIndex.init()
#         LocationIndex.init()
from django.apps import AppConfig


class SearchConfig(AppConfig):
    name = "search"

    def ready(self):
        import search.signals  # 시그널 핸들러가 등록되도록 함
