from elasticsearch import Elasticsearch
from elasticsearch_dsl import Document, Keyword, Text, connections

# Elasticsearch 서버에 연결 설정
connections.create_connection(hosts=["http://localhost:9200"])


# 게시물(Post) 모델에 대한 Elasticsearch 인덱스 정의
class PostIndex(Document):
    # 필드 정의: user_id는 키워드(정확한 값 검색에 사용), title과 content는 텍스트(전문 검색에 사용)
    user_id = Keyword()
    title = Text()
    content = Text()
    thumbnail = Keyword()  # 썸네일 URL은 키워드로 저장

    class Index:
        name = "posts"  # 인덱스 이름을 "posts"로 설정

    def save(self, **kwargs):
        # 인스턴스를 저장할 때 부모 클래스의 save 메서드를 호출
        return super(PostIndex, self).save(**kwargs)


# 위치(Location) 모델에 대한 Elasticsearch 인덱스 정의
class LocationIndex(Document):
    # 필드 정의: city, description, highlights는 텍스트 필드로 정의
    city = Text()
    description = Text()
    highlights = Text()

    class Index:
        name = "locations"  # 인덱스 이름을 "locations"로 설정

    def save(self, **kwargs):
        # 인스턴스를 저장할 때 부모 클래스의 save 메서드를 호출
        return super(LocationIndex, self).save(**kwargs)


# 사용자(User) 모델에 대한 Elasticsearch 인덱스 정의
class UserIndex(Document):
    # 필드 정의: nickname과 email은 텍스트 필드로 정의
    nickname = Text()
    email = Text()

    class Index:
        name = "users"  # 인덱스 이름을 "users"로 설정

    def save(self, **kwargs):
        # 인스턴스를 저장할 때 부모 클래스의 save 메서드를 호출
        return super(UserIndex, self).save(**kwargs)
