# from django.db import models
# from django.contrib.auth.models import User

# class Profile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     nickname = models.CharField(max_length=100, blank=True)
#     email = models.EmailField()
#     password = models.CharField(max_length=128)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.nickname or self.user.username

# users/models.py

from django.contrib.auth.models import AbstractUser  # 장고 모델기능 확장
from django.db import models


class User(AbstractUser):
    # 일반로그인 사용자_이메일, 패스워드
    email = models.EmailField(
        unique=True, null=True, blank=True
    )  # 소셜일 경우 null, blank
    password = models.CharField(max_length=128, blank=True, null=True)
    provider = models.CharField(
        max_length=20, null=False
    )  # 소셜 로그인 제공자 (e.g., 'google', 'kakao', 'naver', 'email')
    social_id = models.CharField(
        max_length=100, null=True, blank=True
    )  # 소셜 로그인 ID
    created_at = models.DateTimeField(auto_now_add=True)  # 계정생성일자,시간등
    nickname = models.CharField(
        max_length=100, null=False, unique=True
    )  # 사용자 이름 저장 unique 제약 조건 추가
    profile_image_url = models.URLField(
        blank=True, null=True
    )  # 프로필 이미지 URL 추가, 소셜에서 이미지 가져오기위함

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["provider", "social_id"], name="unique_provider_social_id"
            )
        ]

    # str메서드 이용해서 객체를 표시할때 닉네임 반환
    def __str__(self):
        return self.nickname


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile"
    )  # User모델과 1:1관계
    introduction = models.TextField(blank=True)  # 자기소개... (이거 논의해야함)
    is_social = models.BooleanField(default=False)  # 소셜 로그인 여부

    def __str__(self):
        return self.nickname if self.nickname else f"Profile of {self.user.username}"


class ProfileImage(models.Model):
    # FK이용해서 user모델과 N:1관계 명시(한 사용자가 여러개의 프로필이미지)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="profile_images"
    )
    image_url = models.CharField(
        max_length=500, null=False
    )  # 문자열 타입, 최대 길이 제한
    is_active = models.BooleanField(default=False)  # 현재사용중인 이미지 여부
    created_at = models.DateTimeField(auto_now_add=True)  # 이미지 업로드 시간 자동저장

    class Meta:
        indexes = [
            models.Index(fields=["user", "is_active"])  # 사용자별 활성 이미지 빠른 조회
        ]
