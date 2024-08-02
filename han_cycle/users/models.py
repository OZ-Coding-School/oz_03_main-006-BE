from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from search.search_index import UserIndex
import uuid
from .managers import CustomUserManager  # Import the custom manager
from django.conf import settings
import datetime

class User(AbstractUser):
    email = models.EmailField(unique=True)  # Unique
    provider = models.CharField(max_length=100)  # Not null
    nickname = models.CharField(max_length=100, unique=True)  # Unique, not null
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    created_at = models.DateTimeField(
        default=timezone.now
    )  # Timestamp with default value of now
    profile_image = models.ImageField(
        upload_to="profile_images/", null=True, blank=True
    )

    #ERD를 기반으로 유저내임 대신 닉네임으로 로그인 처리
    USERNAME_FIELD = "nickname"
    REQUIRED_FIELDS = ["email"]  # Added email to required fields

    objects = CustomUserManager()  # Set the custom manager

    def indexing(self):
        obj = UserIndex(meta={"id": self.id}, nickname=self.nickname, email=self.email)
        obj.save()
        return obj.to_dict(include_meta=True)
    

#엑세스 토큰 만료를 위해 리프레쉬 토큰 클래스 생성
class RefreshToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    #토큰 만료 여부 확인
    def is_expired(self):
        return datetime.datetime.utcnow() > self.expires_at
