from django.apps import apps
from elasticsearch_dsl import Date, Document, Text


class PostIndex(Document):
    title = Text()
    content = Text()

    class Index:
        name = "posts"

    @classmethod
    def get_model(cls):
        return apps.get_model("boards", "Post")


class UserIndex(Document):
    nickname = Text()
    email = Text()

    class Index:
        name = "users"

    @classmethod
    def get_model(cls):
        return apps.get_model("users", "User")


class LocationIndex(Document):
    city = Text()
    description = Text()
    highlights = Text()

    class Index:
        name = "locations"

    @classmethod
    def get_model(cls):
        return apps.get_model("locations", "Location")
