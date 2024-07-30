from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Keyword, Text, connections

# Connect to the Elasticsearch server
connections.create_connection(hosts=["http://localhost:9200"])


class PostIndex(Document):
    user_id = Keyword()
    title = Text()
    content = Text()

    class Index:
        name = "posts"

    def save(self, **kwargs):
        return super(PostIndex, self).save(**kwargs)


class LocationIndex(Document):
    city = Text()
    description = Text()
    highlights = Text()

    class Index:
        name = "locations"

    def save(self, **kwargs):
        return super(LocationIndex, self).save(**kwargs)


class UserIndex(Document):
    nickname = Text()
    email = Text()

    class Index:
        name = "users"

    def save(self, **kwargs):
        return super(UserIndex, self).save(**kwargs)
