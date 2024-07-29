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
            "password",  # Ensure password is included for creation
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "username": {"required": False, "allow_blank": True},  # Allow blank usernames
        }

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("This nickname is already taken.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already taken.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        username = validated_data.get("username")
        
        # Generate a default username if it is not provided
        if not username:
            validated_data["username"] = self.generate_default_username(validated_data["email"])

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def generate_default_username(self, email):
        # Generate a username based on the email if username is not provided
        base_username = email.split('@')[0]
        count = 1
        username = base_username
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{count}"
            count += 1
        return username
