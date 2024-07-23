from elasticsearch_dsl import Date, Document, Text
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["http://elasticsearch:9200"])


class ArticleIndex(Document):
    title = Text()
    content = Text()
    published_date = Date()

    class Index:
        name = "articles"

    def save(self, **kwargs):
        if not self.meta.id:
            self.meta.id = self.id  # self.id가 정의되어 있는지 확인 필요
        return super().save(**kwargs)


# 인덱스 생성 코드 추가
ArticleIndex.init()
