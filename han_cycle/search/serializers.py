from rest_framework import serializers
from users.models import User  # User 모델을 users 애플리케이션에서 가져옴


# 사용자 정보를 업데이트하기 위한 시리얼라이저 정의
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User  # 이 시리얼라이저가 참조할 모델은 User 모델
        fields = [
            "nickname",
            "email",
            "first_name",
            "last_name",
            "bio",
        ]  # 업데이트할 필드 목록
