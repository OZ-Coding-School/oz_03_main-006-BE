from django.apps import apps
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError as DocumentNotFoundError

from .search_index import LocationIndex, PostIndex, UserIndex

# Elasticsearch 인덱스에서 문서를 검색하려고 시도했지만, 해당 문서가 존재하지 않거나 삭제된 경우에 이 예외 발생


# 게시글(Post) 모델의 저장 후 신호를 처리하는 수신기
@receiver(post_save, sender=apps.get_model("boards", "Post"))
def index_post(sender, instance, **kwargs):
    post_index = PostIndex(
        meta={"id": instance.id},  # 인덱스 ID 설정
        title=instance.title,  # 게시글 제목
        content=instance.content,  # 게시글 내용
    )
    post_index.save()


# 게시글(Post) 모델의 삭제 후 신호를 처리하는 수신기
@receiver(post_delete, sender=apps.get_model("boards", "Post"))
def remove_post_from_index(sender, instance, **kwargs):
    try:
        PostIndex.get(id=instance.id).delete()
    except DocumentNotFoundError:
        pass  # 문서가 이미 삭제된 경우 예외 무시


# 사용자(User) 모델의 저장 후 신호를 처리하는 수신기
@receiver(post_save, sender=apps.get_model("users", "User"))
def index_user(sender, instance, **kwargs):
    user_index = UserIndex(
        meta={"id": instance.id},  # 인덱스 ID 설정
        nickname=instance.nickname,  # 사용자 닉네임
        email=instance.email,  # 사용자 이메일
    )
    user_index.save()


# 사용자(User) 모델의 삭제 후 신호를 처리하는 수신기
@receiver(post_delete, sender=apps.get_model("users", "User"))
def remove_user_from_index(sender, instance, **kwargs):
    try:
        UserIndex.get(id=instance.id).delete()
    except DocumentNotFoundError:
        pass  # 문서가 이미 삭제된 경우 예외 무시


# 위치(Location) 모델의 저장 후 신호를 처리하는 수신기
@receiver(post_save, sender=apps.get_model("locations", "Location"))
def index_location(sender, instance, **kwargs):
    location_index = LocationIndex(
        meta={"id": instance.id},  # 인덱스 ID 설정
        city=instance.city,  # 위치 도시
        description=instance.description,  # 위치 설명
        highlights=instance.highlights,  # 위치 하이라이트
    )
    location_index.save()


# 위치(Location) 모델의 삭제 후 신호를 처리하는 수신기
@receiver(post_delete, sender=apps.get_model("locations", "Location"))
def remove_location_from_index(sender, instance, **kwargs):
    try:
        LocationIndex.get(id=instance.id).delete()
    except DocumentNotFoundError:
        pass  # 문서가 이미 삭제된 경우 예외 무시
