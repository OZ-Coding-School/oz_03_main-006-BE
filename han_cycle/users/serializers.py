from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "nickname",
            "profile_image",
            "email",
            "username",
            "password",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True
            },  # 보안을 위해 사용자에게 비밀번호를 반환하지 않음
            "email": {"required": True},
            "username": {
                "required": False,
                "allow_blank": True,
            },  # ERD를 기준으로 닉네임을 유저네임 대신 쓰기때문에 유저네임은 공백가능
        }

    # 닉네임 유효성 검사 (중복 검사)
    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("This nickname is already taken.")
        return value

    # 비밀번호 8자리 이상 유효성 검사
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    # 이메일 중복성 검사
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    # 유효성 검사를 통과한 데이터에서 비밀번호 추출 및 유저네임 처리
    def create(self, validated_data):
        password = validated_data.pop(
            "password", None
        )  # 비밀번호가 없는 경우 none 리턴
        username = validated_data.get("username")

        # 사용자 이름이 없는 경우 유니크한 사용자 이름 생성
        if not username:
            validated_data["username"] = self.generate_default_username(
                validated_data["email"]
            )

        # 사용자 인스턴스 생성
        instance = self.Meta.model(**validated_data)

        # 비밀번호 해시화 후 객체 저장 및 반환
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def generate_default_username(self, email):
        # 이메일 주소에서 @의 앞부분을 기본 사용자 이름으로 생성
        base_username = email.split("@")[0]
        # 사용자 이름 중복 확인 및 수정; 중복된 경우 숫자를 추가하여 고유의 사용자 이름 생성
        count = 1
        username = base_username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{count}"
            count += 1
        return username


# 비밀번호를 찾기위해 이메일 요구
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


# 비밀번호를 새로 설정하기 위해 토큰과 새 비밀번호 요구
class PasswordResetConfirmSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, min_length=8)
