from rest_framework import serializers
from users.models import User  # Bring the user model from users folder

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'email', 'first_name', 'last_name', 'bio']  # update field
