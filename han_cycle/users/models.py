from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nickname or self.user.username


# from django.contrib.auth.models import AbstractUser
# from django.db import models


# class User(AbstractUser):  # 사용자 모델 (소셜 로그인/일반 로그인 모두 지원)
#     """
#     사용자 모델.
#     소셜 로그인 또는 이메일/비밀번호를 통한 회원가입을 지원
#     """

#     email = models.EmailField(
#         unique=True, null=True, blank=True
#     )  # 이메일 (선택 사항, 중복 불가)
#     password = models.CharField(
#         max_length=128, null=True, blank=True
#     )  # 비밀번호 (선택 사항)
#     provider = models.CharField(
#         max_length=20, null=False
#     )  # 소셜 로그인 제공자 (e.g., 'google', 'kakao', 'naver', 'email')
#     social_id = models.CharField(
#         max_length=100, null=True, blank=True
#     )  # 소셜 로그인 ID (선택 사항)
#     nickname = models.CharField(
#         max_length=100, null=False, unique=True
#     )  # 사용자 닉네임 (필수, 중복 불가)
#     created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간

#     # provider와 social_id를 합쳐 unique 제약 조건 생성
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["provider", "social_id"], name="unique_provider_social_id"
#             )
#         ]

#     def __str__(self):
#         return self.nickname


# class Profile(models.Model):
#     """
#     사용자 프로필 정보 모델.
#     """

#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
#     introduction = models.TextField(blank=True)  # 자기소개
#     is_social = models.BooleanField(default=False)  # 소셜 로그인 여부

#     def __str__(self):
#         return self.user.nickname or f"Profile of {self.user.username}"


# class ProfileImage(models.Model):
#     # FK이용해서 user모델과 N:1관계 명시(한 사용자가 여러개의 프로필이미지)
#     user = models.ForeignKey(
#         User, on_delete=models.CASCADE, related_name="profile_images"
#     )
#     image_url = models.CharField(
#         max_length=500, null=False
#     )  # 문자열 타입, 최대 길이 제한
#     is_active = models.BooleanField(default=False)  # 현재사용중인 이미지 여부
#     created_at = models.DateTimeField(auto_now_add=True)  # 이미지 업로드 시간 자동저장

#     class Meta:
#         indexes = [
#             models.Index(fields=["user", "is_active"])  # 사용자별 활성 이미지 빠른 조회
#         ]
