from django.db import models
from elasticsearch_dsl import Date, Document, Text, connections

# Elasticsearch 연결 설정 (URL에 'http://' 포함)
connections.create_connection(hosts=["http://elasticsearch:9200"])

# 게시글을 Elasticsearch에 저장하기 위한 인덱스 정의
class PostIndex(Document):
    title = Text()  # 제목 필드 (Elasticsearch의 Text 타입)
    content = Text()  # 내용 필드 (Elasticsearch의 Text 타입)
    created_at = Date()  # 생성 날짜 필드 (Elasticsearch의 Date 타입)

    class Index:
        name = "posts"  # 인덱스 이름 설정

    def save(self, **kwargs):
        """
        문서를 저장하는 메서드.
        Elasticsearch에 문서를 저장하기 위해 상위 클래스의 save 메서드를 호출합니다.
        """
        return super().save(**kwargs)

# 사용자 정보를 Elasticsearch에 저장하기 위한 인덱스 정의
class UserIndex(Document):
    nickname = Text()  # 닉네임 필드 (Elasticsearch의 Text 타입)
    email = Text()  # 이메일 필드 (Elasticsearch의 Text 타입)

    class Index:
        name = "users"  # 인덱스 이름 설정

    def save(self, **kwargs):
        """
        문서를 저장하는 메서드.
        Elasticsearch에 문서를 저장하기 위해 상위 클래스의 save 메서드를 호출합니다.
        """
        return super().save(**kwargs)

# 위치 정보를 Elasticsearch에 저장하기 위한 인덱스 정의
class LocationIndex(Document):
    city = Text()  # 도시 이름 필드 (Elasticsearch의 Text 타입)
    description = Text()  # 설명 필드 (Elasticsearch의 Text 타입)
    highlights = Text()  # 하이라이트 필드 (Elasticsearch의 Text 타입)

    class Index:
        name = "locations"  # 인덱스 이름 설정

    def save(self, **kwargs):
        """
        문서를 저장하는 메서드.
        Elasticsearch에 문서를 저장하기 위해 상위 클래스의 save 메서드를 호출합니다.
        """
        return super().save(**kwargs)