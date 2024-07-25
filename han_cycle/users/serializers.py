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
        ]  # 'user_id' 대신 'id'를 사용
        extra_kwargs = {"password": {"write_only": True}}

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    # Password requirement validation
    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    # Create method to handle hashed password
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
