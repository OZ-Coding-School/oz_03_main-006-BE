from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = User

        fields = ['nickname', 'user_id', 'profile_image', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_nickname(self, value):
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError("This nickname is already taken.")

        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError(
                "Password must be at least 8 characters long."
            )
        return value

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.username = instance.nickname  
        instance.save()
        return instance


    def validate(self, data):
        """
        Object level validation.
        """
        if 'nickname' in data and 'password' in data:
            if User.objects.filter(nickname=data['nickname']).exists():
                raise serializers.ValidationError("This nickname is already taken.")
            if len(data['password']) < 8:
                raise serializers.ValidationError("Password must be at least 8 characters long.")
        return data

